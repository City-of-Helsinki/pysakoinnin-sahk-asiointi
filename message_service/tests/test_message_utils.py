from unittest.mock import patch

import pytest
from resilient_logger.models import ResilientLogEntry
from suomifi_messages.errors import SuomiFiAPIError

from message_service.enums import DeliveryStatus
from message_service.models import DeliveryReport, Message
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


@pytest.fixture
def client():
    with patch("message_service.utils.SuomiFiClient", autospec=True) as client:
        yield client.return_value


@pytest.fixture
def email_backend():
    with patch("message_service.models.EmailMultiAlternatives") as email_backend:
        yield email_backend.return_value


ATV_RESPONSE_OK = {
    "count": 1,
    "results": [
        {
            "user_id": "user-uuid-123",
            "content": {"ssn": "210281-9988", "email": "test@example.com"},
        }
    ],
}

ATV_RESPONSE_NOT_FOUND = {"count": 0, "results": []}

ATV_RESPONSE_MISSING_FIELDS = {
    "count": 1,
    "results": [{"user_id": None, "content": {"ssn": None, "email": None}}],
}


# get_user_details_by_transaction_id tests


@pytest.mark.django_db
def test_get_user_details_returns_tuple(get_document_by_transaction_id_mock):
    get_document_by_transaction_id_mock.return_value = ATV_RESPONSE_OK
    user_id, ssn, email = get_user_details_by_transaction_id("113148474")
    assert user_id == "user-uuid-123"
    assert ssn == "210281-9988"
    assert email == "test@example.com"


@pytest.mark.django_db
def test_get_user_details_raises_when_not_found(get_document_by_transaction_id_mock):
    get_document_by_transaction_id_mock.return_value = ATV_RESPONSE_NOT_FOUND
    with pytest.raises(TransactionContactInformationError, match="not found"):
        get_user_details_by_transaction_id("113148474")


@pytest.mark.django_db
def test_get_user_details_raises_when_fields_missing(
    get_document_by_transaction_id_mock,
):
    get_document_by_transaction_id_mock.return_value = ATV_RESPONSE_MISSING_FIELDS
    with pytest.raises(TransactionContactInformationError, match="did not contain"):
        get_user_details_by_transaction_id("113148474")


#  Message.send() tests


@pytest.mark.django_db
def test_send_message_via_suomifi(
    message,
    get_document_by_transaction_id_mock,
    client,
):
    get_document_by_transaction_id_mock.return_value = ATV_RESPONSE_OK
    client.check_mailbox.return_value = True
    client.send_electronic_message.return_value = (42, None)

    assert message.send() is True

    client.send_electronic_message.assert_called_once()

    report = DeliveryReport.objects.get(transaction_id=message.transaction_id)
    assert report.status == DeliveryStatus.SENT_SUOMIFI
    assert report.suomifi_id == 42
    assert report.sent_at is not None

    assert ResilientLogEntry.objects.filter(
        context__actor__name="SYSTEM",
        context__target__name="user_id",
        context__target__value="user-uuid-123",
        context__operation="SEND_SUOMIFI",
        message="extend-due-date",
    ).exists()

    assert not Message.objects.filter(pk=message.pk).exists()


@pytest.mark.django_db
def test_send_message_via_email_fallback(
    message,
    get_document_by_transaction_id_mock,
    client,
    email_backend,
):
    get_document_by_transaction_id_mock.return_value = ATV_RESPONSE_OK
    client.check_mailbox.return_value = False

    assert message.send() is True

    email_backend.send.assert_called_once()

    report = DeliveryReport.objects.get(transaction_id=message.transaction_id)
    assert report.status == DeliveryStatus.SENT_EMAIL
    assert report.sent_at is not None

    assert ResilientLogEntry.objects.filter(
        context__actor__name="SYSTEM",
        context__target__name="user_id",
        context__target__value="user-uuid-123",
        context__operation="SEND_MAIL",
        message="extend-due-date",
    ).exists()

    assert not Message.objects.filter(pk=message.pk).exists()


@pytest.mark.django_db
def test_send_message_contact_info_error(message, get_document_by_transaction_id_mock):
    get_document_by_transaction_id_mock.return_value = ATV_RESPONSE_NOT_FOUND
    assert message.send() is False

    message.refresh_from_db()
    assert message.send_failure_count == 1
    assert message.queued is True


@pytest.mark.django_db
def test_send_message_suomifi_error_queues_and_does_not_raise(
    message, get_document_by_transaction_id_mock, client
):
    get_document_by_transaction_id_mock.return_value = ATV_RESPONSE_OK
    client.check_mailbox.side_effect = SuomiFiAPIError("boom")

    assert message.send() is False

    message.refresh_from_db()
    assert message.send_failure_count == 1
    assert message.queued is True


@pytest.mark.django_db
def test_send_message_unexpected_error_queues_and_increments(
    message, get_document_by_transaction_id_mock, client
):
    get_document_by_transaction_id_mock.return_value = ATV_RESPONSE_OK
    client.check_mailbox.side_effect = RuntimeError("unexpected")

    assert message.send() is False

    message.refresh_from_db()
    assert message.send_failure_count == 1
    assert message.queued is True
