import logging

from django.core.management.base import BaseCommand
from mailer.models import PRIORITY_LOW, Message

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Attempt to resend any deferred mail at lower priority."

    def handle(self, *args, **options):
        count = Message.objects.retry_deferred(PRIORITY_LOW)
        logger.info(f"{count} message(s) retried")
