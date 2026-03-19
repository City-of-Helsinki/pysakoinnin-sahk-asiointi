import datetime
import logging
import uuid
from typing import Self

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.db import models
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone, translation
from django.utils.translation import gettext_lazy as _
from resilient_logger.sources import ResilientLogSource
from suomifi_messages.client import SuomiFiClient
from suomifi_messages.schemas import BodyFormat

from api.enums import DocumentStatusEnum
from message_service import utils
from message_service.enums import DeliveryStatus, MessageType
from message_service.utils import (
    EmailSendReturnedZeroError,
    PermanentSendError,
    TransactionContactInformationError,
    TransientSendError,
)

logger = logging.getLogger(__name__)


class Message(models.Model):
    # One-to-one reverse relation
    delivery_report: "DeliveryReport"

    created_at = models.DateTimeField(auto_now_add=True)

    transaction_id = models.CharField()
    queued = models.BooleanField(default=False)
    subject = models.TextField()
    body_text = models.TextField()
    body_html = models.TextField()
    send_failure_count = models.IntegerField(default=0)
    external_id = models.UUIDField(default=uuid.uuid4, unique=True)
    audit_action = models.CharField(max_length=64, default="")
    message_type = models.TextField(choices=MessageType, default=MessageType.OTHER)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(message_type__in=MessageType.values),
                name="check_valid_message_type",
            )
        ]

    def get_or_create_delivery_report(self):
        try:
            return self.delivery_report
        except DeliveryReport.DoesNotExist:
            return DeliveryReport.objects.create(
                transaction_id=self.transaction_id,
                queued_message=self,
                message_type=self.message_type,
            )

    def send(self) -> None:
        """
        Attempts to send the message via Suomi.fi or email fallback.

        If message is sent successfully, the delivery report will be created/updated,
        audit log will be written and the instance will delete itself.

        If sending is unsuccessful, the delivery report will not be created/updated,
        send_failure_count will be incremented and the method will raise either
        TransientSendError or PermanentSendError.

        :raises TransientSendError: If send failed but a retry might succeed
        :raises PermanentSendError: If send failed but retry will not succeed

        """

        try:
            user_id, ssn, email = utils.get_user_details_by_transaction_id(
                self.transaction_id
            )
            client = utils.create_suomifi_client()
            if client.check_mailbox(ssn):
                self._send_suomifi(client, user_id, ssn)
            else:
                self._send_email(user_id, email)

        except (
            TransactionContactInformationError,
            EmailSendReturnedZeroError,
        ) as ex:
            self.send_failure_count += 1
            self.save()
            raise PermanentSendError from ex

        except Exception as ex:
            self.send_failure_count += 1
            self.save()
            raise TransientSendError from ex

    def commit_to_audit_log(self, user_id: str, operation: str):
        ResilientLogSource.create_structured(
            level=logging.NOTSET,
            message=self.audit_action,
            actor={"name": "SYSTEM", "value": ""},
            target={"name": "user_id", "value": user_id},
            operation=operation,
        )

    def _send_suomifi(self, client: SuomiFiClient, user_id: str, ssn: str) -> None:
        suomifi_id, _ = client.send_electronic_message(
            title=self.subject,
            body=self.body_text,
            body_format=BodyFormat.TEXT,
            recipient_id=ssn,
            external_id=str(self.external_id),
        )
        report = self.get_or_create_delivery_report()
        report.sent_at = timezone.now()
        report.status = DeliveryStatus.SENT_SUOMIFI
        report.suomifi_id = suomifi_id
        report.save()
        self.commit_to_audit_log(user_id, "SEND_SUOMIFI")
        self.delete()

    def _send_email(self, user_id: str, email: str) -> None:
        send_immediately_connection = get_connection(settings.MAILER_EMAIL_BACKEND)
        msg = EmailMultiAlternatives(
            self.subject,
            self.body_text,
            f"Pysäköinnin Asiointi <{settings.DEFAULT_FROM_EMAIL}>",
            [email],
            connection=send_immediately_connection,
        )
        msg.attach_alternative(self.body_html, "text/html")
        sent_count = msg.send()
        if not sent_count:
            # Probably a bug or a misconfiguration if we end up here
            raise EmailSendReturnedZeroError()
        report = self.get_or_create_delivery_report()
        report.sent_at = timezone.now()
        report.status = DeliveryStatus.SENT_EMAIL
        report.save()
        self.commit_to_audit_log(user_id, "SEND_MAIL")
        self.delete()

    @classmethod
    def event_message(
        cls, transaction_id: str, event: DocumentStatusEnum, lang: str
    ) -> Self:
        if lang not in ("fi", "sv", "en"):
            lang = "fi"

        with translation.override(lang):
            context = {
                "event": utils.status_label(event),
                "lang": lang,
                "now": timezone.now().astimezone(utils.helsinki_tz).strftime("%H:%M"),
                "url": "https://pysakoinninasiointi.hel.fi",
            }

            msg = cls(
                transaction_id=transaction_id,
                audit_action="set-document-status",
                subject=str(_("New event in Parking e-service")),
                body_text=render_to_string("message_service/event_body.txt", context),
                body_html=render_to_string("message_service/event_body.html", context),
                message_type=MessageType.from_document_status(event),
            )
            msg.save()
            return msg

    @classmethod
    def due_date_extended_message(
        cls, transaction_id: str, new_due_date: str, lang: str
    ) -> Self:
        date = datetime.datetime.strptime(new_due_date, "%Y-%m-%dT%H:%M:%S")
        formatted_due_date = datetime.datetime.strftime(date, "%d.%m.%Y")

        if lang not in ("fi", "sv", "en"):
            lang = "fi"

        with translation.override(lang):
            context = {
                "formatted_due_date": formatted_due_date,
                "lang": lang,
                "url": "https://pysakoinninasiointi.hel.fi",
            }
            msg = cls(
                transaction_id=transaction_id,
                audit_action="extend-due-date",
                subject=str(_("New event in Parking e-service")),
                body_text=render_to_string(
                    "message_service/due_date_extended_body.txt", context
                ),
                body_html=render_to_string(
                    "message_service/due_date_extended_body.html", context
                ),
                message_type=MessageType.DUE_DATE_EXTENDED,
            )
            msg.save()
            return msg


class DeliveryReport(models.Model):
    queued_message = models.OneToOneField(
        Message, null=True, on_delete=models.SET_NULL, related_name="delivery_report"
    )

    transaction_id = models.CharField()
    suomifi_id = models.IntegerField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True)
    read_at = models.DateTimeField(null=True)

    status = models.TextField(choices=DeliveryStatus, default=DeliveryStatus.QUEUED)
    message_type = models.TextField(choices=MessageType, default=MessageType.OTHER)


class SuomifiPersistence(models.Model):
    continuation_token = models.TextField()
