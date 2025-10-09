"""
Integration tests for objection-related endpoints.
These tests verify the full request/response cycle including authentication,
business logic validation, and external service integration.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
from ninja.errors import HttpError

from api.tests.mocks import MockResponse

API_ROOT = "/api/v1"


@pytest.mark.django_db
@patch("pysakoinnin_sahk_asiointi.urls.AuthBearer.authenticate")
@patch("api.views.ATVHandler.add_document")
@patch("api.views.PASIHandler.save_objection")
class TestSaveObjectionEndpoint:
    """Integration tests for saveObjection endpoint."""

    def test_save_objection_with_foul_number(
        self, handler_mock, add_doc_mock, auth_mock, authenticated_client, user
    ):
        """Test saveObjection successfully processes objection with foulNumber."""
        auth_mock.return_value = MagicMock(user=user)

        objection_data = {
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
        }

        handler_mock.return_value = MockResponse(200, {})
        add_doc_mock.return_value = MockResponse(200, {})

        response = authenticated_client.post(
            f"{API_ROOT}/saveObjection",
            data=json.dumps(objection_data),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer fake-token",
        )

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
            "transferNumber": 67890,
            "ssn": "0",
            "firstName": "Jane",
            "lastName": "Smith",
            "email": "jane.smith@example.com",
            "mobilePhone": "+358401234567",
            "iban": "0",
            "authorRole": 2,
            "address": {
                "streetAddress": "Test Street 2",
                "postCode": "00200",
            },
            "description": "Transfer objection",
            "type": 1,
            "sendDecisionViaEService": False,
        }

        handler_mock.return_value = MockResponse(200, {})
        add_doc_mock.return_value = MockResponse(200, {})

        response = authenticated_client.post(
            f"{API_ROOT}/saveObjection",
            data=json.dumps(objection_data),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer fake-token",
        )

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
            "description": "Invalid objection",
            "type": 0,
            "sendDecisionViaEService": True,
        }

        handler_mock.return_value = MockResponse(200, {})
        add_doc_mock.return_value = MockResponse(200, {})

        response = authenticated_client.post(
            f"{API_ROOT}/saveObjection",
            data=json.dumps(objection_data),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer fake-token",
        )

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
            "description": "Objection with metadata",
            "type": 0,
            "sendDecisionViaEService": True,
            "metadata": {"lang": "sv", "source": "web"},
        }

        handler_mock.return_value = MockResponse(200, {})
        add_doc_mock.return_value = MockResponse(200, {})

        response = authenticated_client.post(
            f"{API_ROOT}/saveObjection",
            data=json.dumps(objection_data),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer fake-token",
        )

        assert response.status_code == 200
        # Verify metadata was passed to ATV
        call_kwargs = add_doc_mock.call_args.kwargs
        assert call_kwargs.get("metadata") == {"lang": "sv", "source": "web"}

    @patch("api.api.virus_scan_attachment_file")
    def test_save_objection_with_attachments_triggers_virus_scan(
        self, virus_scan_mock, handler_mock, add_doc_mock, auth_mock, authenticated_client, user
    ):
        """Test saveObjection calls virus scanner when attachments are present."""
        auth_mock.return_value = MagicMock(user=user)

        objection_data = {
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
            "description": "Objection with attachment",
            "attachments": [
                {
                    "fileName": "document.pdf",
                    "mimeType": "application/pdf",
                    "data": "base64data",
                }
            ],
            "type": 0,
            "sendDecisionViaEService": True,
        }

        handler_mock.return_value = MockResponse(200, {})
        add_doc_mock.return_value = MockResponse(200, {})

        response = authenticated_client.post(
            f"{API_ROOT}/saveObjection",
            data=json.dumps(objection_data),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer fake-token",
        )

        assert response.status_code == 200
        virus_scan_mock.assert_called_once_with("base64data")

    @patch("api.api.virus_scan_attachment_file")
    def test_save_objection_virus_scan_failure(
        self, virus_scan_mock, handler_mock, add_doc_mock, auth_mock, authenticated_client, user
    ):
        """Test saveObjection returns error when virus scan fails."""
        auth_mock.return_value = MagicMock(user=user)
        virus_scan_mock.side_effect = HttpError(400, "Virus detected")

        objection_data = {
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
            "description": "Objection with infected attachment",
            "attachments": [
                {
                    "fileName": "virus.pdf",
                    "mimeType": "application/pdf",
                    "data": "infected_data",
                }
            ],
            "type": 0,
            "sendDecisionViaEService": True,
        }

        response = authenticated_client.post(
            f"{API_ROOT}/saveObjection",
            data=json.dumps(objection_data),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer fake-token",
        )

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
            "description": "Objection that will fail at ATV",
            "type": 0,
            "sendDecisionViaEService": True,
        }

        response = authenticated_client.post(
            f"{API_ROOT}/saveObjection",
            data=json.dumps(objection_data),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer fake-token",
        )

        assert response.status_code == 500
        # PASI handler should not be called if ATV fails
        handler_mock.assert_not_called()

    def test_save_objection_returns_pasi_response_code(
        self, handler_mock, add_doc_mock, auth_mock, authenticated_client, user
    ):
        """Test saveObjection returns the response code from PASI handler."""
        auth_mock.return_value = MagicMock(user=user)

        objection_data = {
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
            "description": "Test PASI response code",
            "type": 0,
            "sendDecisionViaEService": True,
        }

        add_doc_mock.return_value = MockResponse(200, {})
        handler_mock.return_value = MockResponse(200, {})  # PASI returns 200

        response = authenticated_client.post(
            f"{API_ROOT}/saveObjection",
            data=json.dumps(objection_data),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer fake-token",
        )

        # The endpoint returns the status code from PASI
        assert response.status_code == 200
        handler_mock.assert_called_once()
        add_doc_mock.assert_called_once()


@pytest.mark.django_db
class TestSaveObjectionUnauthorized:
    """Tests for unauthorized access to saveObjection endpoint."""

    def test_save_objection_unauthorized(self, api_client):
        """Test saveObjection returns 401 when no authentication is provided."""
        objection_data = {
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
            "description": "Unauthorized objection",
            "type": 0,
            "sendDecisionViaEService": True,
        }

        response = api_client.post(
            f"{API_ROOT}/saveObjection",
            data=json.dumps(objection_data),
            content_type="application/json",
        )

        assert response.status_code == 401
