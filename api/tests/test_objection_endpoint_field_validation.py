import json
from unittest.mock import MagicMock, patch

import pytest
from ninja.errors import HttpError

from api.tests.mocks import MockResponse


def post_objection(client, objection_data):
    """
    Helper function to post an objection to the saveObjection endpoint.

    Args:
        client: The test client (authenticated or not)
        objection_data: Dictionary containing the objection data

    Returns:
        Response object from the POST request
    """
    return client.post(
        "/api/v1/saveObjection",
        data=json.dumps(objection_data),
        content_type="application/json",
        HTTP_AUTHORIZATION="Bearer fake-token",
    )


@pytest.mark.django_db
@patch("pysakoinnin_sahk_asiointi.urls.AuthBearer.authenticate")
@patch("api.views.ATVHandler.add_document")
@patch("api.views.PASIHandler.save_objection")
class TestSaveObjectionEndpoint:
    """Integration tests for saveObjection endpoint."""

    # Valid base objection data that can be modified in individual tests
    VALID_OBJECTION_DATA = {
        "foulNumber": 12345,
        "ssn": "0",
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe@example.com",
        "mobilePhone": "+358401234567",
        "iban": "0",
        "authorRole": 1,
        "address": {
            "streetAddress": "Test Street 1",
            "postCode": "00100",
        },
        "description": "I object to this fine",
        "type": 0,
        "sendDecisionViaEService": True,
        "metadata": {},
    }

    def test_save_objection_with_foul_number(
        self, handler_mock, add_doc_mock, auth_mock, authenticated_client, user
    ):
        """Test saveObjection successfully processes objection with foulNumber."""
        auth_mock.return_value = MagicMock(user=user)

        objection_data = self.VALID_OBJECTION_DATA

        handler_mock.return_value = MockResponse(200, {})
        add_doc_mock.return_value = MockResponse(200, {})

        response = post_objection(authenticated_client, objection_data)

        assert response.status_code == 200
        handler_mock.assert_called_once()
        add_doc_mock.assert_called_once()
        # Verify the objection_id used was the foulNumber
        call_kwargs = add_doc_mock.call_args.kwargs
        assert call_kwargs.get("document_id") == 12345

    def test_save_objection_with_transfer_number(
        self, handler_mock, add_doc_mock, auth_mock, authenticated_client, user
    ):
        """Test saveObjection successfully processes objection with transferNumber."""
        auth_mock.return_value = MagicMock(user=user)

        objection_data = {
            **self.VALID_OBJECTION_DATA,
            "foulNumber": None,  # Remove foulNumber to use transferNumber instead
            "transferNumber": 67890,
        }

        handler_mock.return_value = MockResponse(200, {})
        add_doc_mock.return_value = MockResponse(200, {})

        response = post_objection(authenticated_client, objection_data)

        assert response.status_code == 200
        handler_mock.assert_called_once()
        add_doc_mock.assert_called_once()
        # Verify the objection_id used was the transferNumber
        call_kwargs = add_doc_mock.call_args.kwargs
        assert call_kwargs.get("document_id") == 67890

    def test_save_objection_missing_both_identifiers(
        self, handler_mock, add_doc_mock, auth_mock, authenticated_client, user
    ):
        """Test saveObjection returns 422 when both foulNumber and transferNumber are missing."""
        auth_mock.return_value = MagicMock(user=user)

        objection_data = {
            **self.VALID_OBJECTION_DATA,
            "foulNumber": None,  # Remove both identifiers
            "description": "Invalid objection",
        }

        handler_mock.return_value = MockResponse(200, {})
        add_doc_mock.return_value = MockResponse(200, {})

        response = post_objection(authenticated_client, objection_data)

        assert response.status_code == 422
        # Handlers should not be called if validation fails
        handler_mock.assert_not_called()
        add_doc_mock.assert_not_called()

    def test_save_objection_with_metadata(
        self, handler_mock, add_doc_mock, auth_mock, authenticated_client, user
    ):
        """Test saveObjection correctly passes metadata to ATV."""
        auth_mock.return_value = MagicMock(user=user)

        objection_data = {
            **self.VALID_OBJECTION_DATA,
            "description": "Objection with metadata",
            "metadata": {"lang": "sv", "source": "web"},
        }

        handler_mock.return_value = MockResponse(200, {})
        add_doc_mock.return_value = MockResponse(200, {})

        response = post_objection(authenticated_client, objection_data)

        assert response.status_code == 200
        # Verify metadata was passed to ATV
        call_kwargs = add_doc_mock.call_args.kwargs
        assert call_kwargs.get("metadata") == {"lang": "sv", "source": "web"}

    @patch("api.api.virus_scan_attachment_file")
    def test_save_objection_with_attachments_triggers_virus_scan(
        self,
        virus_scan_mock,
        handler_mock,
        add_doc_mock,
        auth_mock,
        authenticated_client,
        user,
    ):
        """Test saveObjection calls virus scanner when attachments are present."""
        auth_mock.return_value = MagicMock(user=user)

        objection_data = {
            **self.VALID_OBJECTION_DATA,
            "description": "Objection with attachment",
            "attachments": [
                {
                    "fileName": "document.pdf",
                    "mimeType": "application/pdf",
                    "data": "base64data",
                }
            ],
        }

        handler_mock.return_value = MockResponse(200, {})
        add_doc_mock.return_value = MockResponse(200, {})

        response = post_objection(authenticated_client, objection_data)

        assert response.status_code == 200
        virus_scan_mock.assert_called_once_with("base64data")

    @patch("api.api.virus_scan_attachment_file")
    def test_save_objection_virus_scan_failure(
        self,
        virus_scan_mock,
        handler_mock,
        add_doc_mock,
        auth_mock,
        authenticated_client,
        user,
    ):
        """Test saveObjection returns error when virus scan fails."""
        auth_mock.return_value = MagicMock(user=user)
        virus_scan_mock.side_effect = HttpError(400, "Virus detected")

        objection_data = {
            **self.VALID_OBJECTION_DATA,
            "description": "Objection with infected attachment",
            "attachments": [
                {
                    "fileName": "virus.pdf",
                    "mimeType": "application/pdf",
                    "data": "infected_data",
                }
            ],
        }

        response = post_objection(authenticated_client, objection_data)

        assert response.status_code == 400
        # Handlers should not be called if virus scan fails
        handler_mock.assert_not_called()
        add_doc_mock.assert_not_called()

    def test_save_objection_atv_handler_failure(
        self, handler_mock, add_doc_mock, auth_mock, authenticated_client, user
    ):
        """Test saveObjection returns 500 when ATV handler fails."""
        auth_mock.return_value = MagicMock(user=user)
        add_doc_mock.side_effect = Exception("ATV service unavailable")

        objection_data = {
            **self.VALID_OBJECTION_DATA,
            "description": "Objection that will fail at ATV",
        }

        response = post_objection(authenticated_client, objection_data)

        assert response.status_code == 500
        # PASI handler should not be called if ATV fails
        handler_mock.assert_not_called()

    def test_save_objection_with_none_metadata_documents_behavior(
        self, handler_mock, add_doc_mock, auth_mock, authenticated_client, user
    ):
        """Test that None metadata causes TypeError (documenting current behavior)."""
        auth_mock.return_value = MagicMock(user=user)

        objection_data = {
            **self.VALID_OBJECTION_DATA,
            "metadata": None,  # Explicitly test None
        }

        response = post_objection(authenticated_client, objection_data)

        # Document current behavior: expects 500 due to TypeError
        assert response.status_code == 500

    def test_save_objection_with_both_identifiers_uses_foul_number(
        self, handler_mock, add_doc_mock, auth_mock, authenticated_client, user
    ):
        """Test that foulNumber takes precedence when both are provided."""
        auth_mock.return_value = MagicMock(user=user)

        objection_data = {
            **self.VALID_OBJECTION_DATA,
            "transferNumber": 67890,  # Should be ignored
            "description": "Objection with both identifiers",
        }

        handler_mock.return_value = MockResponse(200, {})
        add_doc_mock.return_value = MockResponse(200, {})

        response = post_objection(authenticated_client, objection_data)

        assert response.status_code == 200
        handler_mock.assert_called_once()
        add_doc_mock.assert_called_once()
        call_kwargs = add_doc_mock.call_args.kwargs
        assert call_kwargs.get("document_id") == 12345

    def test_save_objection_with_empty_attachments_list(
        self, handler_mock, add_doc_mock, auth_mock, authenticated_client, user
    ):
        """Test saveObjection handles empty attachments list (vs None)."""
        auth_mock.return_value = MagicMock(user=user)

        objection_data = {
            **self.VALID_OBJECTION_DATA,
            "attachments": None,  # Explicitly test None
        }

        handler_mock.return_value = MockResponse(200, {})
        add_doc_mock.return_value = MockResponse(200, {})

        response = post_objection(authenticated_client, objection_data)
        assert response.status_code == 200


@pytest.mark.django_db
class TestSaveObjectionUnauthorized:
    VALID_OBJECTION_DATA = TestSaveObjectionEndpoint.VALID_OBJECTION_DATA

    def test_save_objection_unauthorized(self, api_client):
        objection_data = {
            **self.VALID_OBJECTION_DATA,
            "description": "Unauthorized objection",
        }

        response = post_objection(api_client, objection_data)

        assert response.status_code == 401
