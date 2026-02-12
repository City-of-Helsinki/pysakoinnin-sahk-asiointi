from datetime import datetime, timedelta
from datetime import timezone as dt_timezone
from io import StringIO
from unittest.mock import patch

import pytest
from django.core.mail import EmailMessage
from django.core.management import call_command
from django.test import TransactionTestCase, override_settings
from django.utils import timezone
from mailer.models import PRIORITY_MEDIUM, Message

from mail_service.management.commands.check_stale_messages import get_working_days_ago


def create_test_message():
    email = EmailMessage(
        subject="Test",
        body="Test body",
        from_email="sender@example.com",
        to=["test@example.com"],
    )
    message = Message()
    message.email = email
    message.priority = PRIORITY_MEDIUM
    message.save()
    return message


class TestGetWorkingDaysAgo:
    @pytest.mark.parametrize(
        "frozen_weekday,days,expected_calendar_days",
        [
            (2, 2, 2),  # Wednesday -> Monday (no weekend)
            (0, 2, 4),  # Monday -> Thursday (skips weekend)
            (1, 2, 4),  # Tuesday -> Friday (skips weekend)
            (4, 2, 2),  # Friday -> Wednesday (no weekend)
            (3, 2, 2),  # Thursday -> Tuesday (no weekend)
            (5, 2, 2),  # Saturday -> Thursday (no weekend)
            (6, 2, 3),  # Sunday -> Thursday (no weekend)
        ],
    )
    def test_skips_weekends_correctly(
        self, frozen_weekday, days, expected_calendar_days
    ):
        base_date = datetime(2026, 1, 5, 12, 0, 0, tzinfo=dt_timezone.utc)  # Monday
        days_to_add = (frozen_weekday - base_date.weekday()) % 7
        frozen_time = base_date + timedelta(days=days_to_add)

        with patch(
            "mail_service.management.commands.check_stale_messages.timezone.now",
            return_value=frozen_time,
        ):
            result = get_working_days_ago(days)
            assert result == frozen_time - timedelta(days=expected_calendar_days)


@override_settings(STALE_MESSAGE_THRESHOLD_DAYS=2)
class TestCheckStaleMessagesCommand(TransactionTestCase):
    def test_no_stale_messages(self):
        out = StringIO()
        call_command("check_stale_messages", stdout=out)
        assert "No stale messages found" in out.getvalue()

    def test_stale_messages_triggers_sentry_error(self):
        old_time = timezone.now() - timedelta(days=10)
        message = create_test_message()
        Message.objects.filter(pk=message.pk).update(when_added=old_time)

        out = StringIO()
        with patch(
            "mail_service.management.commands.check_stale_messages.sentry_sdk.capture_message"
        ) as mock_sentry:
            call_command("check_stale_messages", stdout=out)

            mock_sentry.assert_called_once()
            call_args = mock_sentry.call_args
            assert "stale Message(s)" in call_args[0][0]
            assert call_args[1]["level"] == "error"

        assert "stale Message(s)" in out.getvalue()

    def test_recent_messages_not_flagged(self):
        create_test_message()

        out = StringIO()
        with patch(
            "mail_service.management.commands.check_stale_messages.sentry_sdk.capture_message"
        ) as mock_sentry:
            call_command("check_stale_messages", stdout=out)
            mock_sentry.assert_not_called()

        assert "No stale messages found" in out.getvalue()

    @override_settings(STALE_MESSAGE_THRESHOLD_DAYS=5)
    def test_respects_custom_threshold(self):
        old_time = timezone.now() - timedelta(days=4)
        message = create_test_message()
        Message.objects.filter(pk=message.pk).update(when_added=old_time)

        out = StringIO()
        with patch(
            "mail_service.management.commands.check_stale_messages.sentry_sdk.capture_message"
        ) as mock_sentry:
            call_command("check_stale_messages", stdout=out)
            mock_sentry.assert_not_called()

        assert "No stale messages found" in out.getvalue()
