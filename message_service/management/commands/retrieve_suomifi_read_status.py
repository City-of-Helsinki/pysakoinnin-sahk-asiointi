import logging

from django.core.management.base import BaseCommand
from suomifi_messages.schemas import EventType

from message_service.enums import DeliveryStatus
from message_service.models import DeliveryReport, SuomifiPersistence
from message_service.utils import create_suomifi_client

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Retrieve Suomi.fi message read status events and update delivery reports."

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "--all",
            action="store_true",
            help="Retrieve from the beginning (continuation_token=None).",
        )
        group.add_argument(
            "--continuation-token",
            dest="continuation_token",
            metavar="TOKEN",
            help="Retrieve with a specific continuation token.",
        )

    def handle(self, *args, **options):
        persistence, _ = SuomifiPersistence.objects.get_or_create(pk=1)

        if options["all"]:
            continuation_token = None
        elif options["continuation_token"] is not None:
            continuation_token = options["continuation_token"]
        else:
            continuation_token = persistence.continuation_token or None

        client = create_suomifi_client()
        events, next_token = client.get_events(continuation_token)

        for event in events:
            if event.type == EventType.ELECTRONIC_MESSAGE_READ:
                suomifi_id = event.metadata.message_id

                updated_count = DeliveryReport.objects.filter(
                    suomifi_id=suomifi_id
                ).update(read_at=event.event_time, status=DeliveryStatus.READ_SUOMIFI)
                if updated_count:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"DeliveryReport (suomifi_id={suomifi_id}) marked as read."
                        )
                    )
                else:
                    logger.warning(
                        f"Suomi.fi message with suomifi_id={suomifi_id} was reported "
                        "as read but no associated DeliveryReport was found. "
                        "Therefore the read status has not been added into the "
                        "database."
                    )

        persistence.continuation_token = next_token
        persistence.save()
