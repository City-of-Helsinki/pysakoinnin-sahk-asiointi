import datetime
from unittest.mock import patch

import pytest
from ninja.errors import HttpError
from resilient_logger.models import ResilientLogEntry
from suomifi_messages.errors import (
    SuomiFiAPIError,
)
from syrupy.assertion import SnapshotAssertion

from api.enums import DocumentStatusEnum
from message_service.enums import DeliveryStatus
from message_service.models import DeliveryReport, Message
from message_service.utils import (
    PermanentSendError,
    TransactionContactInformationError,
    TransientSendError,
)


@pytest.fixture
def get_user_details_by_transaction_id_mock():
    with patch("message_service.utils.get_user_details_by_transaction_id") as method:
        method.return_value = ("user_id_from_atv", "ssn_from_atv", "email_from_atv")
        yield method


@pytest.fixture
def client():
    with patch("message_service.utils.SuomiFiClient", autospec=True) as client:
        yield client.return_value


@pytest.fixture
def email_backend():
    with patch("message_service.models.EmailMultiAlternatives") as email_backend:
        yield email_backend.return_value


@pytest.mark.django_db
@pytest.mark.parametrize("lang", ["fi", "sv", "en"])
@pytest.mark.parametrize("status", list(DocumentStatusEnum))
def test_event_message(
    freezer, snapshot: SnapshotAssertion, status: DocumentStatusEnum, lang: str
):
    freezer.move_to(
        datetime.datetime(2025, 6, 15, 12, 30, 0, tzinfo=datetime.timezone.utc)
    )
    message = Message.event_message("1", status, lang)
    assert (message.subject, message.body_html, message.body_text) == snapshot


@pytest.mark.django_db
@pytest.mark.parametrize("lang", ["fi", "sv", "en"])
def test_due_date_extended_message(snapshot: SnapshotAssertion, lang: str):
    message = Message.due_date_extended_message("1", "2025-07-01T00:00:00", lang)
    assert (message.subject, message.body_html, message.body_text) == snapshot


@pytest.mark.django_db
def test_send_message_via_suomifi(
    message,
    get_user_details_by_transaction_id_mock,
    client,
):
    client.check_mailbox.return_value = True
    client.send_electronic_message.return_value = (42, None)

    message.send()

    client.send_electronic_message.assert_called_once()

    report = DeliveryReport.objects.get(transaction_id=message.transaction_id)
    assert report.status == DeliveryStatus.SENT_SUOMIFI
    assert report.suomifi_id == 42
    assert report.sent_at is not None

    assert ResilientLogEntry.objects.filter(
        context__actor__name="SYSTEM",
        context__target__name="user_id",
        context__target__value="user_id_from_atv",
        context__operation="SEND_SUOMIFI",
        message="extend-due-date",
    ).exists()

    assert not Message.objects.filter(pk=message.pk).exists()


@pytest.mark.django_db
def test_send_message_via_email_fallback(
    message,
    get_user_details_by_transaction_id_mock,
    client,
    email_backend,
):
    client.check_mailbox.return_value = False

    message.send()

    email_backend.send.assert_called_once()

    report = DeliveryReport.objects.get(transaction_id=message.transaction_id)
    assert report.status == DeliveryStatus.SENT_EMAIL
    assert report.sent_at is not None

    assert ResilientLogEntry.objects.filter(
        context__actor__name="SYSTEM",
        context__target__name="user_id",
        context__target__value="user_id_from_atv",
        context__operation="SEND_MAIL",
        message="extend-due-date",
    ).exists()

    assert not Message.objects.filter(pk=message.pk).exists()


@pytest.mark.django_db
def test_send_message_missing_contact_info_is_permanent_error(
    message,
    get_user_details_by_transaction_id_mock,
):
    get_user_details_by_transaction_id_mock.side_effect = (
        TransactionContactInformationError()
    )
    with pytest.raises(PermanentSendError):
        message.send()

    message.refresh_from_db()
    assert message.send_failure_count == 1


@pytest.mark.django_db
def test_send_message_http_error_is_transient_error(
    message,
    get_user_details_by_transaction_id_mock,
):
    get_user_details_by_transaction_id_mock.side_effect = HttpError(
        500, "Internal server error"
    )
    with pytest.raises(TransientSendError):
        message.send()

    message.refresh_from_db()
    assert message.send_failure_count == 1


@pytest.mark.django_db
def test_send_message_suomifi_error_is_transient(
    message,
    get_user_details_by_transaction_id_mock,
    client,
):
    client.check_mailbox.side_effect = SuomiFiAPIError("boom")

    with pytest.raises(TransientSendError):
        message.send()

    message.refresh_from_db()
    assert message.send_failure_count == 1


@pytest.mark.django_db
def test_send_message_unexpected_error_is_transient(
    message,
    get_user_details_by_transaction_id_mock,
    client,
):
    client.check_mailbox.side_effect = RuntimeError("unexpected")

    with pytest.raises(TransientSendError):
        message.send()

    message.refresh_from_db()
    assert message.send_failure_count == 1
