from datetime import timedelta

import sentry_sdk
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from message_service.enums import DeliveryStatus
from message_service.models import Message
from message_service.utils import PermanentSendError, TransientSendError


class Command(BaseCommand):
    help = "Send all queued messages."

    def handle(self, *args, **options):
        messages = Message.objects.filter(queued=True)
        self.stdout.write(f"Queued message count: {messages.count()}")

        for message in messages:
            if timezone.now() - message.created_at > timedelta(
                hours=settings.SUOMIFI_SEND_RETRY_HOURS
            ):
                self.stdout.write(
                    self.style.WARNING(
                        f"Message {message.pk} for transaction "
                        f"{message.transaction_id} has been removed from the queue as "
                        "it exceeded the retry window of "
                        f"{settings.SUOMIFI_SEND_RETRY_HOURS} hours."
                    )
                )
                self.unqueue_and_report_failed(message)
                continue
            try:
                message.send()
                self.stdout.write(self.style.SUCCESS(f"Message (pk={message.pk}) sent"))
            except TransientSendError as ex:
                sentry_sdk.capture_exception(ex)
                self.stdout.write(
                    self.style.WARNING(
                        f"Message (pk={message.pk}) failed transiently (attempt "
                        f"{message.send_failure_count})"
                    )
                )
            except PermanentSendError as ex:
                sentry_sdk.capture_exception(ex)
                self.stdout.write(
                    self.style.WARNING(
                        f"Message (pk={message.pk}) failed permanently (attempt "
                        f"{message.send_failure_count})"
                    )
                )
                self.unqueue_and_report_failed(message)

    def unqueue_and_report_failed(self, message: Message) -> None:
        message.queued = False
        report = message.get_or_create_delivery_report()
        report.status = DeliveryStatus.FAILED
        message.save()
        report.save()
