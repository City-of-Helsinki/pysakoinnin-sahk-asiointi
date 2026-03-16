import datetime
from datetime import timedelta

import pytest
from syrupy.assertion import SnapshotAssertion

from api.enums import DocumentStatusEnum
from message_service.enums import DeliveryStatus
from message_service.models import Message


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
def test_queue_retry_within_retry_window(message, freezer, settings):
    settings.SUOMIFI_SEND_RETRY_HOURS = 24
    freezer.move_to(
        message.created_at + timedelta(hours=settings.SUOMIFI_SEND_RETRY_HOURS - 1)
    )
    message._queue_retry()

    message.refresh_from_db()
    assert message.queued is True
    assert message.send_failure_count == 1


@pytest.mark.django_db
def test_queue_retry_past_retry_window(message, freezer, settings):
    settings.SUOMIFI_SEND_RETRY_HOURS = 24
    freezer.move_to(
        message.created_at + timedelta(hours=settings.SUOMIFI_SEND_RETRY_HOURS + 1)
    )
    message._queue_retry()

    message.refresh_from_db()
    assert message.queued is False
    assert message.send_failure_count == 1
    assert message.delivery_report.status == DeliveryStatus.FAILED
