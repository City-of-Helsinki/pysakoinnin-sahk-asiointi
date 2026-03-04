import datetime

import pytest
from syrupy.assertion import SnapshotAssertion

from api.schemas import DocumentStatusEnum
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
