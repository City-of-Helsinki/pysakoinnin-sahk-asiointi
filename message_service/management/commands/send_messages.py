from django.core.management.base import BaseCommand

from message_service.models import Message


class Command(BaseCommand):
    help = "Send all queued messages."

    def handle(self, *args, **options):
        messages = Message.objects.filter(queued=True)
        count = messages.count()

        self.stdout.write(f"Queued message count: {count}")

        for message in messages:
            if message.send():
                self.stdout.write(self.style.SUCCESS(f"Message (pk={message.pk}) sent"))
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Message (pk={message.pk}) failed (attempt "
                        f"{message.send_attempt_count})"
                    )
                )
