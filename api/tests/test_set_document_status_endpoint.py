import json
from copy import deepcopy
from unittest.mock import patch

import pytest

VALID_DOCUMENT_STATUS_DATA = {"id": "12345", "status": "handling"}

MOCK_ATV_DOCUMENT_RESPONSE = {
    "results": [
        {
            "id": "12345",
            "metadata": {"lang": "fi"},
            "content": {"email": "test@example.com"},
        }
    ]
}


@pytest.fixture(autouse=True)
def setup_pasi_api_key(settings):
    settings.PASI_API_KEY = "PASI_TOKEN"


@pytest.mark.django_db
@patch("api.views.DocumentHandler.set_document_status")
@patch("api.views.ATVHandler.get_document_by_transaction_id")
def test_set_document_status_endpoint(
    get_document_mock,
    set_status_mock,
    client,
    user,
):
    data = deepcopy(VALID_DOCUMENT_STATUS_DATA)

    get_document_mock.return_value = MOCK_ATV_DOCUMENT_RESPONSE
    set_status_mock.return_value = None

    response = client.patch(
        "/api/v1/setDocumentStatus",
        data=json.dumps(data),
        content_type="application/json",
        HTTP_AUTHORIZATION="Bearer PASI_TOKEN",
    )

    assert response.status_code == 200

    get_document_mock.assert_called_once()
    set_status_mock.assert_called_once()


@pytest.mark.django_db
def test_set_document_status_endpoint_unauthorized(client):
    data = deepcopy(VALID_DOCUMENT_STATUS_DATA)

    response = client.patch(
        "/api/v1/setDocumentStatus",
        data=json.dumps(data),
        content_type="application/json",
    )

    assert response.status_code == 401
