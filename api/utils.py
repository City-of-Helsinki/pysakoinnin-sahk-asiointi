import base64
import logging

import requests
from django.conf import settings
from ninja.errors import HttpError

from api.enums import DocumentStatusEnum
from api.schemas import DocumentStatusRequest
from mail_service.audit_log import _commit_to_audit_log
from mail_service.utils import mail_constructor
from message_service.models import Message
from message_service.utils import PermanentSendError, TransientSendError

logger = logging.getLogger(__name__)


def virus_scan_attachment_file(file_data):
    try:
        response = requests.post(
            settings.CLAMAV_HOST,
            files={"FILES": base64.b64decode(file_data + "==")},
            timeout=settings.OUTGOING_REQUEST_TIMEOUT,
        )
        response_json = response.json()
        if (
            hasattr(response_json, "data")
            and response_json["data"]["result"][0]["is_infected"] is True
        ):
            raise HttpError(422, message="File is infected")
        return response_json
    except HttpError as error:
        return error


def send_document_status_notification(document, status_request: DocumentStatusRequest):
    if settings.SUOMIFI_MESSAGES_ENABLED:
        lang = document["results"][0]["metadata"]["lang"]
        message = Message.event_message(status_request.id, status_request.status, lang)
        if status_request.status == DocumentStatusEnum.received:
            try:
                message.send()
            except TransientSendError:
                message.queued = True
                message.save()
                logger.exception(
                    "Transiently failed to send document status message, queued for "
                    "retry."
                )
            except PermanentSendError:
                logger.exception("Permanently failed to send document status message.")

        else:
            message.queued = True
            message.save()

    else:
        mail = mail_constructor(
            event=status_request.status,
            lang=document["results"][0]["metadata"]["lang"],
            mail_to=document["results"][0]["content"]["email"],
        )
        mail.send()
        _commit_to_audit_log(mail.to[0], "set-document-status")
