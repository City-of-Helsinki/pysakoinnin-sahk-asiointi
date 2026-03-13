from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command

from message_service.models import Message


@pytest.mark.django_db
def test_send_messages_command(message):
    message.queued = True
    message.save()

    with patch.object(Message, "send", return_value=True) as mock_send:
        out = StringIO()
        call_command("send_messages", stdout=out)

    mock_send.assert_called_once()
    output = out.getvalue()
    assert "1" in output
    assert str(message.pk) in output
