import json
import logging
from unittest.mock import MagicMock, patch

import pytest
from resilient_logger.models import ResilientLogEntry
from resilient_logger.sources import ResilientLogSource

from api.audit_log import _get_operation_name, _get_status, _get_user_id
from api.enums import Operation, Status
from api.tests.mocks import MockResponse


@pytest.mark.django_db
@patch("pysakoinnin_sahk_asiointi.urls.AuthBearer.authenticate")
class TestAuditLogMiddleware:
    """Tests for audit logging middleware on API endpoints."""

    def assert_log_entry(
        self,
        log_entry,
        status,
        operation,
        path_contains,
        user_uuid=None,
        origin="pysakoinnin-sahkoinen-asiointi-api",
    ):
        """Helper method to assert common audit log entry properties."""
        assert log_entry.message == status
        assert log_entry.level == logging.NOTSET
        assert log_entry.context["operation"] == operation
        assert path_contains in log_entry.context["target"]["value"]
        assert log_entry.context["actor"]["name"] == "user_id"
        assert log_entry.context["actor"]["value"] == user_uuid

        document = ResilientLogSource(log_entry).get_document()
        assert document["audit_event"]["origin"] == origin

        document = ResilientLogSource(log_entry).get_document()
        assert document["audit_event"]["origin"] == origin
        assert document["audit_event"]["level"] == logging.NOTSET

    @patch("api.views.PASIHandler.get_foul_data")
    def test_get_request_is_audit_logged_with_read_operation(
        self,
        pasi_mock,
        auth_mock,
        authenticated_client,
        user,
        valid_foul_data_response,
    ):
        """Test that GET requests are logged with READ operation."""
        auth_mock.return_value = MagicMock(user=user)
        pasi_mock.return_value = MockResponse(200, valid_foul_data_response)

        response = authenticated_client.get(
            "/api/v1/getFoulData?foul_number=12345&register_number=HKR-999",
            HTTP_AUTHORIZATION="Bearer fake-token",
        )

        assert response.status_code == 200

        # Verify audit log entry in database
        log_entries = ResilientLogEntry.objects.all()
        assert log_entries.count() == 1
        self.assert_log_entry(
            log_entries.first(),
            Status.SUCCESS.value,
            Operation.READ.value,
            "/api/v1/getFoulData",
            str(user.uuid),
        )

    @patch("api.views.ATVHandler.add_document")
    @patch("api.views.PASIHandler.save_objection")
    def test_post_request_is_audit_logged_with_create_operation(
        self,
        pasi_mock,
        atv_mock,
        auth_mock,
        authenticated_client,
        user,
        valid_objection_data,
    ):
        """Test that POST requests are logged with CREATE operation."""
        auth_mock.return_value = MagicMock(user=user)
        pasi_mock.return_value = MockResponse(200, {})
        atv_mock.return_value = MockResponse(200, {})

        response = authenticated_client.post(
            "/api/v1/saveObjection",
            data=json.dumps(valid_objection_data),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer fake-token",
        )

        assert response.status_code == 200

        # Verify audit log entry in database
        log_entries = ResilientLogEntry.objects.all()
        assert log_entries.count() == 1
        self.assert_log_entry(
            log_entries.first(),
            Status.SUCCESS.value,
            Operation.CREATE.value,
            "/api/v1/saveObjection",
            str(user.uuid),
        )

    @patch("api.views.ATVHandler.get_document_by_transaction_id")
    @patch("api.views.DocumentHandler.set_document_status")
    @patch("api.api.mail_constructor")
    def test_patch_request_is_audit_logged_with_update_operation(
        self,
        mail_mock,
        doc_handler_mock,
        atv_mock,
        auth_mock,
        authenticated_client,
        user,
        settings,
    ):
        """Test that PATCH requests are logged with UPDATE operation."""
        auth_mock.return_value = MagicMock(user=user)
        settings.PASI_API_KEY = "test-api-key"
        atv_mock.return_value = {
            "results": [
                {
                    "id": "doc-123",
                    "metadata": {"lang": "fi"},
                    "content": {"email": "test@example.com"},
                }
            ]
        }
        doc_handler_mock.return_value = MockResponse(200, {})
        mock_mail = MagicMock()
        mock_mail.to = ["test@example.com"]
        mail_mock.return_value = mock_mail

        response = authenticated_client.patch(
            "/api/v1/setDocumentStatus",
            data=json.dumps({"id": "transaction-123", "status": "received"}),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer test-api-key",
        )

        assert response.status_code == 200

        # Verify audit log entry in database - find the middleware entry (UPDATE operation)
        log_entries = ResilientLogEntry.objects.filter(
            context__operation=Operation.UPDATE.value
        )
        assert log_entries.count() == 1
        self.assert_log_entry(
            log_entries.first(),
            Status.SUCCESS.value,
            Operation.UPDATE.value,
            "/api/v1/setDocumentStatus",
            str(user.uuid),
        )

    def test_unauthorized_request_is_audit_logged_with_forbidden_status(
        self,
        auth_mock,
        api_client,
        valid_objection_data,
    ):
        """Test that 401 responses are logged with FORBIDDEN status."""
        # Don't mock auth - let it actually fail
        auth_mock.return_value = None

        response = api_client.post(
            "/api/v1/saveObjection",
            data=json.dumps(valid_objection_data),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer invalid-token",
        )

        assert response.status_code == 401

        # Verify audit log entry in database
        log_entries = ResilientLogEntry.objects.all()
        assert log_entries.count() == 1
        self.assert_log_entry(
            log_entries.first(),
            Status.FORBIDDEN.value,
            Operation.CREATE.value,
            "/api/v1/saveObjection",
            None,
        )

    def test_request_without_authorization_header_is_audit_logged(
        self,
        auth_mock,
        api_client,
        valid_objection_data,
    ):
        """Test that requests without Authorization header are logged with FORBIDDEN status."""
        auth_mock.return_value = None

        response = api_client.post(
            "/api/v1/saveObjection",
            data=json.dumps(valid_objection_data),
            content_type="application/json",
        )

        assert response.status_code == 401

        # Verify audit log entry in database
        log_entries = ResilientLogEntry.objects.all()
        assert log_entries.count() == 1
        self.assert_log_entry(
            log_entries.first(),
            Status.FORBIDDEN.value,
            Operation.CREATE.value,
            "/api/v1/saveObjection",
            None,
        )

    @patch("api.views.ATVHandler.add_document")
    def test_failed_request_is_audit_logged_with_failed_status(
        self,
        atv_mock,
        auth_mock,
        authenticated_client,
        user,
        valid_objection_data,
    ):
        """Test that 500 responses are logged with FAILED status."""
        auth_mock.return_value = MagicMock(user=user)
        atv_mock.side_effect = Exception("Service unavailable")

        response = authenticated_client.post(
            "/api/v1/saveObjection",
            data=json.dumps(valid_objection_data),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer fake-token",
        )

        assert response.status_code == 500

        # Verify audit log entry in database
        log_entries = ResilientLogEntry.objects.all()
        assert log_entries.count() == 1
        self.assert_log_entry(
            log_entries.first(),
            Status.FAILED.value,
            Operation.CREATE.value,
            "/api/v1/saveObjection",
            str(user.uuid),
        )

    @patch("api.views.ATVHandler.add_document")
    @patch("api.views.PASIHandler.save_objection")
    def test_validation_error_is_audit_logged_with_failed_status(
        self,
        pasi_mock,
        atv_mock,
        auth_mock,
        authenticated_client,
        user,
        valid_objection_data,
    ):
        """Test that 422 validation errors are logged with FAILED status."""
        auth_mock.return_value = MagicMock(user=user)
        pasi_mock.return_value = MockResponse(200, {})
        atv_mock.return_value = MockResponse(200, {})

        invalid_data = {**valid_objection_data, "foulNumber": None}

        response = authenticated_client.post(
            "/api/v1/saveObjection",
            data=json.dumps(invalid_data),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer fake-token",
        )

        assert response.status_code == 422

        # Verify audit log entry in database
        log_entries = ResilientLogEntry.objects.all()
        assert log_entries.count() == 1
        self.assert_log_entry(
            log_entries.first(),
            Status.FAILED.value,
            Operation.CREATE.value,
            "/api/v1/saveObjection",
            str(user.uuid),
        )

    def test_malformed_json_request_is_audit_logged_with_failed_status(
        self,
        auth_mock,
        authenticated_client,
        user,
    ):
        """Test that requests with malformed JSON are logged with FAILED status."""
        auth_mock.return_value = MagicMock(user=user)

        response = authenticated_client.post(
            "/api/v1/saveObjection",
            data="{invalid json",
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer fake-token",
        )

        # Should return 400 or 422 for malformed JSON
        assert response.status_code in [400, 422]

        # Verify audit log entry in database
        log_entries = ResilientLogEntry.objects.all()
        assert log_entries.count() == 1
        self.assert_log_entry(
            log_entries.first(),
            Status.FAILED.value,
            Operation.CREATE.value,
            "/api/v1/saveObjection",
            str(user.uuid),
        )

    def test_health_endpoint_is_not_audit_logged(
        self,
        auth_mock,
        api_client,
    ):
        """Test that health check endpoints are excluded from audit logging."""
        api_client.get("/health/")

        # No new audit log entries should be created
        assert ResilientLogEntry.objects.count() == 0

    def test_readiness_endpoint_is_not_audit_logged(
        self,
        auth_mock,
        api_client,
    ):
        """Test that readiness check endpoints are excluded from audit logging."""
        api_client.get("/readiness/")

        # No new audit log entries should be created
        assert ResilientLogEntry.objects.count() == 0

    @patch("api.views.ATVHandler.get_documents")
    def test_request_is_audit_logged_with_correct_origin(
        self,
        atv_mock,
        auth_mock,
        authenticated_client,
        user,
    ):
        """Test that audit log entries include the correct origin."""
        auth_mock.return_value = MagicMock(user=user)
        atv_mock.return_value = {"results": [], "count": 0}

        response = authenticated_client.get(
            "/api/v1/getDocuments/",
            HTTP_AUTHORIZATION="Bearer fake-token",
        )

        assert response.status_code == 200

        # Verify audit log entry includes correct origin
        log_entries = ResilientLogEntry.objects.all()
        assert log_entries.count() == 1
        document = ResilientLogSource(log_entries.first()).get_document()
        assert document["audit_event"]["origin"] == "pysakoinnin-sahkoinen-asiointi-api"

    @patch("api.views.PASIHandler.get_transfer_data")
    def test_get_transfer_data_is_audit_logged(
        self,
        pasi_mock,
        auth_mock,
        authenticated_client,
        user,
        valid_transfer_data_response,
    ):
        """Test that getTransferData endpoint is properly audit logged."""
        auth_mock.return_value = MagicMock(user=user)
        pasi_mock.return_value = MockResponse(200, valid_transfer_data_response)

        response = authenticated_client.get(
            "/api/v1/getTransferData?transfer_number=67890&register_number=HKR-999",
            HTTP_AUTHORIZATION="Bearer fake-token",
        )

        assert response.status_code == 200

        # Verify audit log entry in database
        log_entries = ResilientLogEntry.objects.all()
        assert log_entries.count() == 1
        self.assert_log_entry(
            log_entries.first(),
            Status.SUCCESS.value,
            Operation.READ.value,
            "/api/v1/getTransferData",
            str(user.uuid),
        )

    @patch("api.views.PASIHandler.get_foul_data")
    def test_multiple_requests_create_separate_log_entries(
        self,
        pasi_mock,
        auth_mock,
        authenticated_client,
        user,
        valid_foul_data_response,
    ):
        """Test that multiple requests create separate audit log entries."""
        auth_mock.return_value = MagicMock(user=user)
        pasi_mock.return_value = MockResponse(200, valid_foul_data_response)

        # Make multiple requests
        authenticated_client.get(
            "/api/v1/getFoulData?foul_number=11111&register_number=AAA-111",
            HTTP_AUTHORIZATION="Bearer fake-token",
        )
        authenticated_client.get(
            "/api/v1/getFoulData?foul_number=22222&register_number=BBB-222",
            HTTP_AUTHORIZATION="Bearer fake-token",
        )
        authenticated_client.get(
            "/api/v1/getFoulData?foul_number=33333&register_number=CCC-333",
            HTTP_AUTHORIZATION="Bearer fake-token",
        )

        # Verify each request created a separate log entry
        log_entries = ResilientLogEntry.objects.all()
        assert log_entries.count() == 3
        for log_entry in log_entries:
            assert log_entry.message == Status.SUCCESS.value
            assert log_entry.context["operation"] == Operation.READ.value


class TestAuditLogHelperFunctions:
    """Unit tests for audit log helper functions."""

    @pytest.mark.parametrize(
        "status_code,expected_status",
        [
            (200, Status.SUCCESS.value),
            (201, Status.SUCCESS.value),
            (401, Status.FORBIDDEN.value),
            (403, Status.FORBIDDEN.value),
            (400, Status.FAILED.value),
            (404, Status.FAILED.value),
            (422, Status.FAILED.value),
            (500, Status.FAILED.value),
            (502, Status.FAILED.value),
            (503, Status.FAILED.value),
        ],
    )
    def test_get_status_returns_correct_value(self, status_code, expected_status):
        """Test _get_status returns correct status for various status codes."""
        mock_response = MagicMock()
        mock_response.status_code = status_code

        assert _get_status(mock_response) == expected_status

    @pytest.mark.parametrize(
        "method,expected_operation",
        [
            ("GET", Operation.READ.value),
            ("POST", Operation.CREATE.value),
            ("PUT", Operation.UPDATE.value),
            ("PATCH", Operation.UPDATE.value),
            ("DELETE", Operation.DELETE.value),
        ],
    )
    def test_get_operation_name_returns_correct_value(self, method, expected_operation):
        """Test _get_operation_name returns correct operation for various HTTP methods."""
        mock_request = MagicMock()
        mock_request.method = method

        assert _get_operation_name(mock_request) == expected_operation

    @pytest.mark.parametrize(
        "method",
        ["HEAD", "OPTIONS"],
    )
    def test_get_operation_name_returns_none_for_unsupported_methods(self, method):
        """Test _get_operation_name returns None for unsupported HTTP methods."""
        mock_request = MagicMock()
        mock_request.method = method

        assert _get_operation_name(mock_request) is None

    def test_get_user_id_returns_uuid_string(self):
        """Test _get_user_id returns user UUID as string."""
        from uuid import uuid4

        test_uuid = uuid4()
        mock_request = MagicMock()
        mock_request.user.uuid = test_uuid

        assert _get_user_id(mock_request) == str(test_uuid)

    def test_get_user_id_returns_none_for_anonymous_user(self):
        """Test _get_user_id returns None for user without uuid."""
        mock_request = MagicMock(spec=["user"])
        mock_request.user = MagicMock(spec=[])  # No uuid attribute

        assert _get_user_id(mock_request) is None
