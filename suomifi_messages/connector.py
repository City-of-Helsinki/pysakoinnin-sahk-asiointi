import logging
import uuid

import requests

from django.conf import settings

sfm_logger = logging.getLogger("suomi-fi-messages")


class SuomiFIMessagesConnector:
    token = None
    token_expiry = None
    token_type = None

    session = None  # Python requests session

    URL_BASE = None

    def __init__(self, type="qa"):
        _SUOMIFI_QA_HOST = "https://api.messages-qa.suomi.fi"
        _SUOMIFI_PROD_HOST = "https://api.messages.suomi.fi"

        self.session = requests.Session()

        if type == "prod":
            self.URL_BASE = _SUOMIFI_PROD_HOST
        elif type == "qa":
            self.URL_BASE = _SUOMIFI_QA_HOST
        else:
            raise Exception('Invalid type. Allowed values are "prod" and "qa"')

    def login(self, username: str = None, password: str = None):
        _LOGIN_ENDPOINT = "/v1/token"

        auth_params = {
            "username": username or settings.SUOMIFI_USERNAME,
            "password": password or settings.SUOMIFI_PASSWORD,
        }

        def mask_password(password: str) -> str:
            if password:
                return password[0] + "*" * (len(password) - 1)
            return ""

        sfm_logger.debug(
            f"Logging in with username: {auth_params['username']}, password: {mask_password(auth_params['password'])}"
        )

        response = requests.post(self.URL_BASE + _LOGIN_ENDPOINT, json=auth_params)

        if response.status_code != requests.codes.ok:
            sfm_logger.debug(
                f"Authentication request failed with status code {response.status_code}"
            )
            sfm_logger.debug(response.json())
            raise Exception("Authentication request failed")

        parsed_response = response.json()

        # These are informational only, session header setup below
        # is used for all authorized requests
        self.token = parsed_response["access_token"]
        self.token_expiry = parsed_response["expires_in"]
        self.token_type = parsed_response["token_type"]

        self.session.headers.update(
            {"Authorization": self.token, "Host": "api.messages-qa.suomi.fi"}
        )

    def change_password(self, current_password, new_password):
        _PW_CHANGE_ENDPOINT = "/v1/change-password"

        pw_change_request = {
            "currentPassword": current_password,
            "newPassword": new_password,
            "accessToken": self.token,
        }

        # Password change is a special case that does not use Authorization-header
        response = requests.post(
            self.URL_BASE + _PW_CHANGE_ENDPOINT, json=pw_change_request
        )

        if response.status_code != requests.codes.ok:
            print(response.json())
            raise (Exception("Password change request failed"))

        return response.json()

    def check_mailboxes(self, hetu_list):
        _MAILBOX_CHECK_ENDPOINT = "/v1/mailboxes/active"

        mailbox_activity_request = {"endUsers": [{"id": x} for x in hetu_list]}

        response = self._send_post(_MAILBOX_CHECK_ENDPOINT, mailbox_activity_request)

        return response.json()

    def send_message(
        self,
        title,
        body,
        service_id=None,
        recipient_id=None,
        reply_to=None,
        attachment_ids=[],
        delivery_format="electronic",
        internal_id=None,
        verifiable=False,
        reply_allowed=False,
    ):
        _MSG_MULTIMODAL_SEND_ENDPOINT = "/v1/messages"
        _MSG_ELECTRONIC_SEND_ENDPOINT = "/v1/messages/electronic"

        if service_id is None:
            service_id = settings.SUOMIFI_SERVICE_ID

        if recipient_id is None:
            recipient_id = settings.SUOMIFI_TEST_USER_SSN

        if internal_id is None:
            internal_id = str(uuid.uuid4())

        electronic_msg = {
            "body": body,
            # "attachments": {'fileId': [ x for x in attachment_ids ]},
            "attachments": [],
            "messageServiceType": "Verifiable" if verifiable else "Normal",
            "replyAllowedBy": "Anyone" if reply_allowed else "No one",
            "title": title,
            "notifications": {
                "customisedNewMessageNotification": {
                    "title": {
                        "fi": "string",
                        "sv": "string",
                        "en": "string",
                    },
                    "content": {
                        "fi": "string",
                        "sv": "string",
                        "en": "string",
                    },
                },
                "unreadMessageNotification": {
                    "reminder": "Default reminder",
                },
                "senderDetailsInNotifications": "Organisation and service name",
            },
            "visibility": "Normal",
        }

        if reply_to:
            electronic_msg["inReplyToMessageId"] = reply_to

        paper_msg = {
            "colorPrinting": True,
            "createCoverPage": True,
            "files": {"fileId": [x for x in attachment_ids]},
            "messageServiceType": "Verifiable" if verifiable else "Normal",
            "printingAndEnvelopingService": {
                "postiMessaging": {
                    "contactDetails": {"email": "vastaanottajan@spostiosoite.example"},
                    "password": "posti_username_placeholder",
                    "username": "posti_password_placeholder",
                },
                "costPool": "string",
            },
            "recipient": {
                "address": {
                    "additionalName": "Lisäosoiterivi",
                    "city": "Helsinki",
                    "countryCode": "FI",
                    "name": "Paperipostin vastaanottaja",
                    "streetAddress": "Paperipostin osoite",
                    "zipCode": "Paperipostin postinumero",
                }
            },
            "sender": {
                "address": {
                    "additionalName": "Lisälähettäjä",
                    "city": "Helsinki",
                    "countryCode": "FI",
                    "name": "Helsingin kaupunki",
                    "streetAddress": "Työpajankatu 8",
                    "zipCode": "00100",
                },
            },
        }

        msg_request_head = {
            "externalId": internal_id,  # Identifier in some internal system of our own, checked for duplicates by suomi.fi  # noqa: E501
            "recipient": {
                "id": recipient_id
            },  # HETU or Business ID ("Y-tunnus"?), does not affect paper mail at all
            "sender": {"serviceId": service_id},
        }

        # Electronic message format is always required
        msg_request_head["electronic"] = electronic_msg
        # This endpoint accepts messages without paperMail
        endpoint = _MSG_ELECTRONIC_SEND_ENDPOINT

        if delivery_format == "postal" or delivery_format == "both":
            msg_request_head["paperMail"] = paper_msg
            endpoint = _MSG_MULTIMODAL_SEND_ENDPOINT

        sfm_logger.debug(f"Sending message {msg_request_head}")

        response = self._send_post(endpoint, msg_request_head)

        if response.status_code != requests.codes.ok:
            sfm_logger.debug(
                f"Message send request failed with status code {response.status_code}"
            )
            sfm_logger.debug(response.json())
            raise Exception("Message send request failed")

        return response.json()

    def get_events(self, continuation=None):
        _EVENTV2_ENDPOINT = "/v2/events"

        if continuation:
            response = self._send_get(
                _EVENTV2_ENDPOINT, {"continuationToken": continuation}
            )
        else:
            response = self._send_get(_EVENTV2_ENDPOINT)

        response.raise_for_status()

        return response.json()

    def get_message(self, message_id):
        _MESSAGE_READ_ENDPOINT = "/v1/messages/"

        response = self._send_get(_MESSAGE_READ_ENDPOINT + message_id)

        response.raise_for_status()

        return response.json()

    def get_message_state(self, message_id):
        _MESSAGE_STATE_ENDPOINT = "/v1/messages/{message_id}/state"

        response = self._send_get(_MESSAGE_STATE_ENDPOINT.format(message_id=message_id))

        response.raise_for_status()

        return response.json()

    def get_attachment(self, attachment_id):
        _ATTACHMENT_ENDPOINT = "/v1/attachments/"

        response = self._send_get(_ATTACHMENT_ENDPOINT + attachment_id)

        response.raise_for_status()

        return response

    def add_attachment(self, filelike):
        _ATTACHMENT_ENDPOINT = "/v1/attachments"

        raise NotImplementedError

    def _send_post(self, endpoint, body):
        return self.session.post(self.URL_BASE + endpoint, json=body)

    def _send_get(self, endpoint, params=None):
        return self.session.get(self.URL_BASE + endpoint, params=params)
