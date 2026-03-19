from datetime import timedelta
from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command

from message_service.enums import DeliveryStatus
from message_service.models import Message
from message_service.utils import PermanentSendError, TransientSendError


@pytest.mark.django_db
def test_send_messages_command_send_success(message):
    message.queued = True
    message.save()

    with patch.object(Message, "send") as mock_send:
        out = StringIO()
        call_command("send_messages", stdout=out)

    mock_send.assert_called_once()
    output = out.getvalue()
    assert f"Message (pk={message.pk}) sent" in output


@pytest.mark.django_db
def test_send_messages_command_send_transient_error(message):
    message.queued = True
    message.save()

    with patch.object(Message, "send", side_effect=TransientSendError()) as mock_send:
        out = StringIO()
        call_command("send_messages", stdout=out)

    mock_send.assert_called_once()
    output = out.getvalue()
    assert f"Message (pk={message.pk}) failed transiently" in output

    message.refresh_from_db()
    assert message.queued


@pytest.mark.django_db
def test_send_messages_command_send_permanent_error(message):
    message.queued = True
    message.save()

    with patch.object(Message, "send", side_effect=PermanentSendError()) as mock_send:
        out = StringIO()
        call_command("send_messages", stdout=out)

    mock_send.assert_called_once()
    output = out.getvalue()
    assert f"Message (pk={message.pk}) failed permanently" in output

    message.refresh_from_db()
    assert not message.queued


@pytest.mark.django_db
def test_send_messages_past_retry_window(message, freezer, settings):
    message.queued = True
    message.save()
    settings.SUOMIFI_SEND_RETRY_HOURS = 24
    freezer.move_to(
        message.created_at + timedelta(hours=settings.SUOMIFI_SEND_RETRY_HOURS + 1)
    )
    out = StringIO()
    call_command("send_messages", stdout=out)

    output = out.getvalue()
    assert (
        "has been removed from the queue as it exceeded the retry window of 24 hours"
        in output
    )

    message.refresh_from_db()
    assert message.queued is False
    assert message.send_failure_count == 0
    assert message.delivery_report.status == DeliveryStatus.FAILED
