import logging
from typing import assert_never
from zoneinfo import ZoneInfo

from django.conf import settings
from django.utils.translation import gettext as _
from suomifi_messages.client import SuomiFiClient
from suomifi_messages.schemas import EventType

from api.enums import DocumentStatusEnum
from api.views import ATVHandler
from message_service.enums import DeliveryStatus

logger = logging.getLogger(__name__)

helsinki_tz = ZoneInfo("Europe/Helsinki")


def status_label(event: DocumentStatusEnum) -> str:
    label = None

    match event:
        case DocumentStatusEnum.sent:
            label = _("Sent")
        case DocumentStatusEnum.received:
            label = _("Received")
        case DocumentStatusEnum.handling:
            label = _("In process")
        case DocumentStatusEnum.resolvedViaEService:
            label = _("Decision in e-services")
        case DocumentStatusEnum.resolvedViaMail:
            label = _("Decision has been mailed")
        case _:
            assert_never(event)

    return label


def create_suomifi_client() -> SuomiFiClient:
    client = SuomiFiClient(settings.SUOMIFI_ENVIRONMENT)
    client.login(settings.SUOMIFI_USERNAME, settings.SUOMIFI_PASSWORD)
    return client


class TransactionContactInformationError(Exception):
    pass


def get_user_details_by_transaction_id(transaction_id: str) -> tuple[str, str, str]:
    try:
        response = ATVHandler.get_document_by_transaction_id(transaction_id)
    except Exception as ex:
        raise TransactionContactInformationError("ATV error") from ex

    if not response.get("count"):
        raise TransactionContactInformationError(
            f"Transaction ({transaction_id}) not found"
        )

    for result in response["results"]:
        user_id = result.get("user_id")
        content = result.get("content", {})
        ssn = content.get("ssn")
        email = content.get("email")

        # Assume that all must exist and considering the edge case
        # where only some exist is not worth the effort
        if user_id and ssn and email:
            return user_id, ssn, email

    raise TransactionContactInformationError(
        f"Transaction ({transaction_id}) did not contain user_id, SSN and email"
    )


def check_suomifi_events():
    # TODO: This method will be moved and used in a management command
    from message_service.models import DeliveryReport, SuomifiPersistence

    persistence, _ = SuomifiPersistence.objects.get_or_create(pk=1)
    client = create_suomifi_client()
    events, continuation_token = client.get_events(
        persistence.continuation_token or None
    )

    for event in events:
        if event.type == EventType.ELECTRONIC_MESSAGE_READ:
            suomifi_id = event.metadata.message_id
            try:
                delivery_report = DeliveryReport.objects.get(suomifi_id=suomifi_id)
                delivery_report.read_at = event.event_time
                delivery_report.status = DeliveryStatus.READ_SUOMIFI
                delivery_report.save()
            except DeliveryReport.DoesNotExist:
                logger.warning(
                    f"Suomi.fi message with suomifi_id={suomifi_id} was reported as "
                    "read but no associated DeliveryReport was found. Therefore the "
                    "read status has not been added into the database."
                )

    persistence.continuation_token = continuation_token
    persistence.save()
