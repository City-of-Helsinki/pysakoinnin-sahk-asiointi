import logging
from datetime import timedelta

import sentry_sdk
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from mailer.models import Message

logger = logging.getLogger(__name__)


def get_working_days_ago(days: int) -> timezone.datetime:
    """
    Calculate the datetime that is `days` working days ago.
    Working days are Monday through Friday.
    """
    now = timezone.now()
    current = now
    working_days_counted = 0

    while working_days_counted < days:
        current -= timedelta(days=1)
        # Monday is 0, Friday is 4
        if current.weekday() < 5:
            working_days_counted += 1

    return current


class Command(BaseCommand):
    help = """Check for Message objects older than
    configured working days and report to Sentry."""

    def handle(self, *args, **options):
        threshold = get_working_days_ago(settings.STALE_MESSAGE_THRESHOLD_DAYS)
        stale_messages = Message.objects.filter(when_added__lt=threshold)
        count = stale_messages.count()

        if count > 0:
            error_message = (
                f"Found {count} stale Message(s) in the database older than "
                f"{settings.STALE_MESSAGE_THRESHOLD_DAYS} working days. "
                f"Check email queue."
            )
            logger.error(error_message)
            sentry_sdk.capture_message(error_message, level="error")
            self.stdout.write(self.style.ERROR(error_message))
        else:
            info_message = "No stale messages found."
            logger.info(info_message)
            self.stdout.write(self.style.SUCCESS(info_message))
