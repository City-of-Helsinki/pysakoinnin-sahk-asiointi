from typing import assert_never

from django.db import models
from django.utils.translation import gettext_lazy as _

from api.enums import DocumentStatusEnum


class DeliveryStatus(models.TextChoices):
    QUEUED = "queued", _("Queued")
    SENT_SUOMIFI = "sent_suomifi", _("Sent via Suomi.fi messages")
    SENT_EMAIL = "sent_email", _("Sent via e-mail")
    READ_SUOMIFI = "read_suomifi", _("Read via Suomi.fi messages")
    FAILED = "failed", _("Failed")


class MessageType(models.TextChoices):
    OTHER = "other", _("Other")
    DUE_DATE_EXTENDED = "due_date_extended", _("Due date extended")
    STATUS_SENT = "status_sent", _("Status: sent")
    STATUS_RECEIVED = "status_received", _("Status: received")
    STATUS_HANDLING = "status_handling", _("Status: handling")
    STATUS_RESOLVED_VIA_E_SERVICE = (
        "status_resolved_via_e_service",
        _("Status: resolved via e-service"),
    )
    STATUS_RESOLVED_VIA_MAIL = (
        "status_resolved_via_mail",
        _("Status: resolved via mail"),
    )

    @staticmethod
    def from_document_status(document_status: DocumentStatusEnum) -> "MessageType":
        rv = None

        match document_status:
            case DocumentStatusEnum.sent:
                rv = MessageType.STATUS_SENT
            case DocumentStatusEnum.received:
                rv = MessageType.STATUS_RECEIVED
            case DocumentStatusEnum.handling:
                rv = MessageType.STATUS_HANDLING
            case DocumentStatusEnum.resolvedViaEService:
                rv = MessageType.STATUS_RESOLVED_VIA_E_SERVICE
            case DocumentStatusEnum.resolvedViaMail:
                rv = MessageType.STATUS_RESOLVED_VIA_MAIL
            case _:
                assert_never(document_status)

        return rv
