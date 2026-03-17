import datetime
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command
from suomifi_messages.schemas import EventType

from message_service.enums import DeliveryStatus
from message_service.models import DeliveryReport, SuomifiPersistence


@pytest.fixture
def client():
    with patch("message_service.utils.SuomiFiClient", autospec=True) as client:
        yield client.return_value


def _make_event(event_type, suomifi_id, event_time):
    event = MagicMock()
    event.type = event_type
    event.metadata.message_id = suomifi_id
    event.event_time = event_time
    return event


@pytest.mark.django_db
def test_retrieve_suomifi_read_status_uses_persisted_token_by_default(client):
    SuomifiPersistence.objects.create(pk=1, continuation_token="persisted-token")
    client.get_events.return_value = ([], "new-token")

    call_command("retrieve_suomifi_read_status")

    client.get_events.assert_called_once_with("persisted-token")


@pytest.mark.django_db
def test_retrieve_suomifi_read_status_all_switch_uses_none_token(client):
    SuomifiPersistence.objects.create(pk=1, continuation_token="old-token")
    client.get_events.return_value = ([], "new-token")

    call_command("retrieve_suomifi_read_status", all=True)

    client.get_events.assert_called_once_with(None)


@pytest.mark.django_db
def test_retrieve_suomifi_read_status_continuation_token_switch_uses_arg(client):
    SuomifiPersistence.objects.create(pk=1, continuation_token="old-token")
    client.get_events.return_value = ([], "new-token")

    call_command("retrieve_suomifi_read_status", continuation_token="specific-token")

    client.get_events.assert_called_once_with("specific-token")


@pytest.mark.django_db
def test_retrieve_suomifi_read_status_updates_continuation_token(client):
    client.get_events.return_value = (
        [],
        "some-next-token",
    )
    call_command("retrieve_suomifi_read_status")
    assert SuomifiPersistence.objects.get(pk=1).continuation_token == "some-next-token"


@pytest.mark.django_db
def test_retrieve_suomifi_read_status_marks_read(client):
    report = DeliveryReport.objects.create(transaction_id="tx1", suomifi_id=99)
    assert report.read_at is None

    read_time = datetime.datetime(2025, 6, 1, 12, 0, tzinfo=datetime.timezone.utc)
    client.get_events.return_value = (
        [_make_event(EventType.ELECTRONIC_MESSAGE_READ, 99, read_time)],
        "next-token",
    )
    call_command("retrieve_suomifi_read_status")

    report.refresh_from_db()
    assert report.read_at == read_time
    assert report.status == DeliveryStatus.READ_SUOMIFI


@pytest.mark.django_db
def test_retrieve_suomifi_read_status_ignores_unknown_event_type(client):
    report = DeliveryReport.objects.create(
        transaction_id="tx1", suomifi_id=99, status=DeliveryStatus.SENT_SUOMIFI
    )
    assert report.read_at is None
    client.get_events.return_value = (
        [_make_event("unknown-event-type", 99, datetime.datetime.now())],
        "token-xyz",
    )

    call_command("retrieve_suomifi_read_status")

    report.refresh_from_db()
    assert report.read_at is None
    assert report.status == DeliveryStatus.SENT_SUOMIFI


@pytest.mark.django_db
def test_retrieve_suomifi_read_status_nop_if_no_matching_report(client):
    read_time = datetime.datetime(2025, 6, 1, 12, 0, tzinfo=datetime.timezone.utc)
    client.get_events.return_value = (
        [_make_event(EventType.ELECTRONIC_MESSAGE_READ, 999, read_time)],
        "next-token",
    )

    call_command("retrieve_suomifi_read_status")

    assert not DeliveryReport.objects.filter(suomifi_id=999).exists()
