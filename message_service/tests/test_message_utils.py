import datetime
from unittest.mock import MagicMock, patch

import pytest
from resilient_logger.models import ResilientLogEntry
from suomifi_messages.errors import SuomiFiAPIError
from suomifi_messages.schemas import EventType

from message_service.models import DeliveryReport, Message, SuomifiPersistence
from message_service.utils import (
    TransactionContactInformationError,
    check_suomifi_events,
    get_user_details_by_transaction_id,
)


@pytest.fixture
def message(db):
    return Message.objects.create(
        transaction_id="113148474",
        subject="Test subject",
        body_text="Test body",
        body_html="<p>Test body</p>",
        audit_action="extend-due-date",
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

    message.send()

    client.send_electronic_message.assert_called_once()

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

    message.send()

    email_backend.send.assert_called_once()
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
    message.send()  # must not raise

    message.refresh_from_db()
    assert message.send_attempt_count == 1
    assert message.queued is True


@pytest.mark.django_db
def test_send_message_suomifi_error_queues_and_does_not_raise(
    message, get_document_by_transaction_id_mock, client
):
    get_document_by_transaction_id_mock.return_value = ATV_RESPONSE_OK
    client.check_mailbox.side_effect = SuomiFiAPIError("boom")

    message.send()  # must not raise

    message.refresh_from_db()
    assert message.send_attempt_count == 1
    assert message.queued is True


@pytest.mark.django_db
def test_send_message_unexpected_error_queues_and_increments(
    message, get_document_by_transaction_id_mock, client
):
    get_document_by_transaction_id_mock.return_value = ATV_RESPONSE_OK
    client.check_mailbox.side_effect = RuntimeError("unexpected")

    message.send()  # must not raise

    message.refresh_from_db()
    assert message.send_attempt_count == 1
    assert message.queued is True


# check_suomifi_events tests


def _make_event(event_type, message_id, event_time):
    event = MagicMock()
    event.type = event_type
    event.metadata.message_id = message_id
    event.event_time = event_time
    return event


@pytest.mark.django_db
def test_check_suomifi_events_marks_read(client):
    report = DeliveryReport.objects.create(transaction_id="tx1", suomifi_id=99)
    read_time = datetime.datetime(2025, 6, 1, 12, 0, tzinfo=datetime.timezone.utc)

    client.get_events.return_value = (
        [_make_event(EventType.ELECTRONIC_MESSAGE_READ, 99, read_time)],
        "next-token",
    )

    check_suomifi_events()

    report.refresh_from_db()
    assert report.read_at == read_time
    assert SuomifiPersistence.objects.get(pk=1).continuation_token == "next-token"


@pytest.mark.django_db
def test_check_suomifi_events_ignores_unknown_event_type(client):
    unknown_event = _make_event("some-other-type", 999, datetime.datetime.now())
    client.get_events.return_value = ([unknown_event], "token-xyz")

    check_suomifi_events()  # must not raise

    assert not DeliveryReport.objects.filter(suomifi_id=999).exists()
    assert SuomifiPersistence.objects.get(pk=1).continuation_token == "token-xyz"
