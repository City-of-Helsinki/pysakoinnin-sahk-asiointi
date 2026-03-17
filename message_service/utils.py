import logging
from typing import assert_never
from zoneinfo import ZoneInfo

from django.conf import settings
from django.utils.translation import gettext as _
from suomifi_messages.client import SuomiFiClient

from api.enums import DocumentStatusEnum
from api.views import ATVHandler

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


class EmailSendReturnedZeroError(Exception):
    pass


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
