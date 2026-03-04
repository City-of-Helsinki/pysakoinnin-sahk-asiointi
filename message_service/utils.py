import datetime
import logging
import smtplib
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone, translation
from django.utils.translation import gettext as _
from suomifi_messages.client import SuomiFiClient
from suomifi_messages.errors import SuomiFiError
from suomifi_messages.schemas import BodyFormat

from api.schemas import DocumentStatusEnum
from api.views import ATVHandler
from message_service.models import DeliveryReport, Message, SuomifiPersistence

logger = logging.getLogger(__name__)

helsinki_tz = ZoneInfo("Europe/Helsinki")


def event_message(transaction_id: str, event: DocumentStatusEnum, lang: str) -> Message:
    if lang not in ("fi", "sv", "en"):
        lang = "fi"

    with translation.override(lang):
        context = {
            "event": event.label(),
            "now": timezone.now().astimezone(helsinki_tz).strftime("%H:%M"),
            "url": "https://pysakoinninasiointi.hel.fi",
        }
        # subject =
        # html_message = render_to_string("message_service/event_message.html", context)

        return Message(
            transaction_id=transaction_id,
            subject=_("New event in Parking e-service"),
            body_text=render_to_string("message_service/event_body.txt", context),
            body_html=render_to_string("message_service/event_body.html", context),
        )


def due_date_extended_message(
    transaction_id: str, new_due_date: str, lang: str
) -> Message:
    date = datetime.datetime.strptime(new_due_date, "%Y-%m-%dT%H:%M:%S")
    formatted_due_date = datetime.datetime.strftime(date, "%d.%m.%Y")

    if lang not in ("fi", "sv", "en"):
        lang = "fi"

    with translation.override(lang):
        context = {
            "formatted_due_date": formatted_due_date,
            "url": "https://pysakoinninasiointi.hel.fi",
        }
        return Message(
            subject=_("New event in Parking e-service"),
            body_text=render_to_string(
                "message_service/due_date_extended_body.txt", context
            ),
            body_html=render_to_string(
                "message_service/due_date_extended_body.html", context
            ),
        )


class TransactionContactInformationError(Exception):
    pass


def get_email_and_ssn_by_transaction_id(transaction_id: str) -> tuple[str, str]:
    response = ATVHandler.get_document_by_transaction_id(transaction_id)
    if response.get("count"):
        raise TransactionContactInformationError(
            f"Transaction ({transaction_id}) not found"
        )

    for result in response["results"]:
        content = result.get("content", {})
        ssn = content.get("ssn")
        email = content.get("email")

        # Assume that BOTH should always exist and considering the edge case
        # where only one or the other exists is not worth it
        if ssn and email:
            return ssn, email

    raise TransactionContactInformationError(
        "Transaction ({transaction_id}) did not contain SSN and email"
    )


def create_message(
    transaction_id: str,
    subject_suomifi: str,
    subject_email: str,
    body_suomifi: str,
    body_email: str,
    send_immediately=False,
):
    message = Message.objects.create(
        transaction_id=transaction_id,
        foo="",
        subject_suomifi=subject_suomifi,
        subject_email=subject_email,
        body_suomifi=body_suomifi,
        body_email=body_email,
    )

    _ = message.get_or_create_delivery_report()

    if send_immediately:
        message.send()


def send_message(message: Message):
    try:
        ssn, email = get_email_and_ssn_by_transaction_id(message.transaction_id)
    except TransactionContactInformationError:
        message.send_attempt_count += 1
        message.save()
        # TODO write error report
        # TODO failure point and removal from queue?
        # TODO sentry logging?
        return
    client = SuomiFiClient("qa")
    try:
        if client.check_mailbox(ssn):
            suomifi_id, _ = client.send_electronic_message(
                title=message.subject,
                body=message.body_text,
                body_format=BodyFormat.TEXT,
                recipient_id=ssn,
                external_id=message.external_id,
            )

            report = message.get_or_create_delivery_report()
            report.sent_at = timezone.now()
            report.suomifi_id = suomifi_id
            report.save()
            message.delete()

        else:
            send_immediately_connection = settings.MAILER_EMAIL_BACKEND
            msg = EmailMultiAlternatives(
                message.subject,
                message.body_text,
                f"Pysäköinnin Asiointi <{settings.DEFAULT_FROM_EMAIL}>",
                [email],
                connection=send_immediately_connection,
            )

            msg.attach_alternative(message.body_html, "text/html")
            msg.send()

    except (SuomiFiError, smtplib.SMTPException):
        message.send_attempt_count += 1
        message.save()
        raise


# def send_messages(messages: list[QueuedMessage]):
#     for message in messages:
#         message.send()


def check_suomifi_events():
    persistence, _ = SuomifiPersistence.objects.get_or_create(pk=1)
    client = SuomiFiClient("qa")
    response = client.get_events(persistence.continuation_token)

    for event in response["events"]:
        if event["type"] == "Electronic message read":
            try:
                delivery_report = DeliveryReport.objects.get(
                    suomifi_id=event["metadata"]["messageId"]
                )
                delivery_report.read_at = event["eventTime"]
                delivery_report.save()

            except DeliveryReport.DoesNotExist:
                pass  # TODO

    persistence.continuation_token = response["continuationToken"]
    persistence.save()
