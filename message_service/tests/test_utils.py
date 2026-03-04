import datetime

import pytest
from syrupy.assertion import SnapshotAssertion

from message_service.utils import EventType, due_date_extended_message, event_message

FROZEN_TIME = datetime.datetime(2025, 6, 15, 12, 30, 0, tzinfo=datetime.timezone.utc)
DUE_DATE = "2025-07-01T00:00:00"


@pytest.mark.parametrize("lang", ["fi", "sv", "en"])
@pytest.mark.parametrize("event", list(EventType))
def test_event_message(freezer, snapshot: SnapshotAssertion, event: EventType, lang: str):
    freezer.move_to(FROZEN_TIME)
    subject, html, plain = event_message(event, lang)
    assert (subject, html, plain) == snapshot


@pytest.mark.parametrize("lang", ["fi", "sv", "en"])
def test_due_date_extended_message(snapshot: SnapshotAssertion, lang: str):
    subject, html, plain = due_date_extended_message(DUE_DATE, lang)
    assert (subject, html, plain) == snapshot
