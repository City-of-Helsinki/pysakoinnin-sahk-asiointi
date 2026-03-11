import pytest

from message_service.models import Message


@pytest.fixture
def message(db):
    return Message.due_date_extended_message(
        transaction_id="113148474", new_due_date="2026-03-11T16:51:00", lang="en"
    )
