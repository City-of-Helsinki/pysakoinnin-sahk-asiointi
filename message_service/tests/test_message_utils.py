from unittest.mock import patch

import pytest
from ninja.errors import HttpError

from message_service.utils import (
    TransactionContactInformationError,
    get_user_details_by_transaction_id,
)


@pytest.fixture
def get_document_by_transaction_id_mock():
    with patch(
        "message_service.utils.ATVHandler.get_document_by_transaction_id", autospec=True
    ) as method:
        yield method


@pytest.mark.django_db
def test_get_user_details_returns_tuple(
    get_document_by_transaction_id_mock,
):
    get_document_by_transaction_id_mock.return_value = {
        "count": 1,
        "results": [
            {
                "user_id": "user-uuid-123",
                "content": {"ssn": "210281-9988", "email": "test@example.com"},
            }
        ],
    }

    user_id, ssn, email = get_user_details_by_transaction_id("113148474")
    assert user_id == "user-uuid-123"
    assert ssn == "210281-9988"
    assert email == "test@example.com"


@pytest.mark.django_db
def test_get_user_details_raises_when_not_found(get_document_by_transaction_id_mock):
    get_document_by_transaction_id_mock.side_effect = HttpError(
        404, message="Resource not found"
    )
    with pytest.raises(
        TransactionContactInformationError, match="No data was found from ATV"
    ):
        get_user_details_by_transaction_id("113148474")


@pytest.mark.django_db
def test_get_user_details_raises_if_response_500(get_document_by_transaction_id_mock):
    get_document_by_transaction_id_mock.side_effect = HttpError(
        500, message="Internal server error"
    )
    with pytest.raises(HttpError, match="Internal server error"):
        get_user_details_by_transaction_id("113148474")


@pytest.mark.django_db
def test_get_user_details_raises_when_fields_missing(
    get_document_by_transaction_id_mock,
):
    get_document_by_transaction_id_mock.return_value = {
        "count": 1,
        "results": [{"user_id": None, "content": {"ssn": None, "email": None}}],
    }

    with pytest.raises(TransactionContactInformationError, match="did not contain"):
        get_user_details_by_transaction_id("113148474")
