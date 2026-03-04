import datetime
import logging
import smtplib
import uuid
from typing import Self

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone, translation
from django.utils.translation import gettext_lazy as _
from resilient_logger.sources import ResilientLogSource
from suomifi_messages.errors import SuomiFiAPIError
from suomifi_messages.schemas import BodyFormat

from api.schemas import DocumentStatusEnum
from message_service import utils

logger = logging.getLogger(__name__)


class Message(models.Model):
    # One-to-one reverse relation
    delivery_report: "DeliveryReport"

    transaction_id = models.CharField()
    queued = models.BooleanField(default=False)
    subject = models.TextField()
    body_text = models.TextField()
    body_html = models.TextField()
    send_attempt_count = models.IntegerField(default=0)
    external_id = models.UUIDField(default=uuid.uuid4)
    audit_action = models.CharField(max_length=64, default="")

    def get_or_create_delivery_report(self):
        try:
            return self.delivery_report
        except DeliveryReport.DoesNotExist:
            return DeliveryReport.objects.create(
                transaction_id=self.transaction_id, queued_message=self
            )

    def send(self):
        """
        Attempts to send the message via Suomi.fi or email fallback.
        On any failure, ensures the message is saved with queued=True so it
        can be retried and does not remain in unqueued limbo.
        """

        try:
            user_id, ssn, email = utils.get_user_details_by_transaction_id(
                self.transaction_id
            )
        except utils.TransactionContactInformationError:
            logger.exception("Unable to send: contact information error")
            self._queue_with_increment()
            return

        client = utils.create_suomifi_client()
        try:
            if client.check_mailbox(ssn):
                suomifi_id, _ = client.send_electronic_message(
                    title=self.subject,
                    body=self.body_text,
                    body_format=BodyFormat.TEXT,
                    recipient_id=ssn,
                    external_id=str(self.external_id),
                )
                report = self.get_or_create_delivery_report()
                report.sent_at = timezone.now()
                report.suomifi_id = suomifi_id
                report.save()
                self.commit_to_audit_log(user_id, self.audit_action, "SEND_SUOMIFI")
                self.delete()
            else:
                send_immediately_connection = get_connection(
                    settings.MAILER_EMAIL_BACKEND
                )
                msg = EmailMultiAlternatives(
                    self.subject,
                    self.body_text,
                    f"Pysäköinnin Asiointi <{settings.DEFAULT_FROM_EMAIL}>",
                    [email],
                    connection=send_immediately_connection,
                )
                msg.attach_alternative(self.body_html, "text/html")
                msg.send()
                self.commit_to_audit_log(user_id, self.audit_action, "SEND_MAIL")
                self.delete()
        except (SuomiFiAPIError, smtplib.SMTPException, Exception):
            logger.exception("Error sending message")
            self._queue_with_increment()

    def _queue_with_increment(self):
        """Increments attempt count, ensures queued=True, and saves."""
        self.send_attempt_count += 1
        self.queued = True
        self.save()

    def commit_to_audit_log(self, user_id: str, action: str, operation: str):
        ResilientLogSource.create_structured(
            level=logging.NOTSET,
            message=action,
            actor={"name": "SYSTEM", "value": ""},
            target={"name": "user_id", "value": user_id},
            operation=operation,
        )

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
            )
            msg.save()
            return msg


class DeliveryReport(models.Model):
    class DeliveryStatus(models.TextChoices):
        QUEUED = "queued", _("Queued")
        SENT_SUOMIFI = "sent_suomifi", _("Sent via Suomi.fi messages")
        SENT_EMAIL = "sent_email", _("Sent via e-mail")
        FAILED = "failed", _("Failed")

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


class SuomifiPersistence(models.Model):
    continuation_token = models.TextField()
