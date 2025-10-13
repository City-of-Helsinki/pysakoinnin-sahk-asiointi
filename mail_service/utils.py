import datetime
import logging
from zoneinfo import ZoneInfo

from anymail.message import attach_inline_image_file
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from mailer import engine

from mail_service import audit_log

QUEUE_EMAIL_CONNECTION = settings.EMAIL_BACKEND
SEND_INSTANTLY_EMAIL_CONNECTION = settings.MAILER_EMAIL_BACKEND

logger = logging.getLogger(__name__)
headers = {
    "FI": "Uusi tapahtuma Pysäköinnin Asioinnissa",
    "SV": "Nya händelser i parkering e-tjänsten",
    "EN": "New event in Parking e-service",
}

events = {
    "received": {"FI": "Vastaanotettu", "SV": "Mottaget", "EN": "Received"},
    "handling": {"FI": "Käsittelyssä", "SV": "Bearbetning", "EN": "In process"},
    "resolvedViaEService": {
        "FI": "Päätös asioinnissa",
        "SV": "Beslut i e-tjänster",
        "EN": "Decision in e-services",
    },
    "resolvedViaMail": {
        "FI": "Päätös postitettu",
        "SV": "Beslutsbrev postat",
        "EN": "Decision has been mailed",
    },
}


# If the event status indicates that the user is actively interacting with the client,
# we want to send emails instantly. Therefore, return "SEND_INSTANTLY_EMAIL_CONNECTION".
# Otherwise, if the user is not interacting with the client, use the email queue.
def get_email_connection(event: str):
    if event == "received":
        return get_connection(SEND_INSTANTLY_EMAIL_CONNECTION)
    return get_connection(QUEUE_EMAIL_CONNECTION)


def mail_constructor(event: str, lang: str, mail_to: str):
    now = datetime.datetime.now(tz=ZoneInfo("Europe/Helsinki"))
    formatted_time = datetime.datetime.strftime(now, "%H:%M")
    connection = get_email_connection(event)
    if lang not in headers:
        lang = "FI"

    body_templates = {
        "FI": (
            "<p>"
            "Pysäköinnin asiointiin on saapunut uusi tapahtuma:"
            " <i>{event}</i> klo {now}."
            "<br>"
            "Kirjaudu pysäköinnin sähköiseen asiointiin"
            " https://pysakoinninasiointi.hel.fi"
            "<br>"
            "<br>"
            "(Tämä on automaattinen viesti jonka on lähettänyt Helsingin kaupungin"
            " pysäköinninvalvonnan sähköinen asiointipalvelu. Älä vastaa tähän"
            " viestiin.)"
            "</p>"
        ).format(event=events[event][lang.upper()], now=formatted_time),
        "SV": (
            "<p>"
            "Nya händelser har kommit in i parkering e-tjänsten:"
            " <i>{event}</i> på {now}."
            "<br>"
            "Logga in på parkerings e-tjänster https://pysakoinninasiointi.hel.fi"
            "<br>"
            "<br>"
            "(Detta är ett automatiskt meddelande som skickas av Helsingfors stads"
            " parkeringsövervaknings e-tjänst. Svara inte på detta meddelande.)"
            "</p>"
        ).format(event=events[event][lang.upper()], now=formatted_time),
        "EN": (
            "<p>"
            "New event has arrived in the Parking e-service: <i>{event}</i> at {now}."
            "<br>"
            "Sign in to parking e-services https://pysakoinninasiointi.hel.fi"
            "<br>"
            "<br>"
            "(This is an automated message sent by the City of Helsinki parking control"
            " e-service. Do not reply to this message.)"
            "</p>"
        ).format(event=events[event][lang.upper()], now=formatted_time),
    }

    msg = EmailMultiAlternatives(
        headers[lang.upper()],
        body_templates[lang.upper()],
        f"Pysäköinnin Asiointi <{settings.DEFAULT_FROM_EMAIL}>",
        [mail_to],
        connection=connection,
    )

    logo = attach_inline_image_file(msg, "mail_service/assets/logo.jpg")
    html = """
    <html>
    <body>
    <h2><img alt="Logo" src="cid:{logo}" height="24px" style="margin-right: 12px;"/>Pysäköinnin
        Asiointi</h2>
    <h1>{header}</h1>
    {body}
    </body>
    </html>""".format(  # noqa: E501
        header=headers[lang.upper()], body=body_templates[lang.upper()], logo=logo
    )

    msg.attach_alternative(html, "text/html")

    return msg


def extend_due_date_mail_constructor(lang: str, new_due_date: str, mail_to):
    date = datetime.datetime.strptime(new_due_date, "%Y-%m-%dT%H:%M:%S")
    formatted_time = datetime.datetime.strftime(date, "%d.%m.%Y")
    connection = get_connection(SEND_INSTANTLY_EMAIL_CONNECTION)

    body_templates = {
        "FI": "<p>Eräpäivää siirretty, uusi eräpäivä on {new_due_date}".format(
            new_due_date=formatted_time
        ),
        "SV": (
            "<p>Förfallodagen har skjutits upp. Nytt förfallodag är {new_due_date}"
        ).format(new_due_date=formatted_time),
        "EN": (
            "<p>The due date has been postponed. New due date is {new_due_date}"
        ).format(new_due_date=formatted_time),
    }
    if lang not in body_templates:
        lang = "FI"

    msg = EmailMultiAlternatives(
        headers[lang.upper()],
        body_templates[lang.upper()],
        f"Pysäköinnin Asiointi <{settings.DEFAULT_FROM_EMAIL}>",
        [mail_to],
        connection=connection,
    )

    logo = attach_inline_image_file(msg, "mail_service/assets/logo.jpg")
    html = """
    <html>
    <body>
    <h2><img alt="Logo" src="cid:{logo}" height="24px" style="margin-right: 12px;"/>Pysäköinnin
        Asiointi</h2>
    <h1>{header}</h1>
    {body}
    </body>
    </html>""".format(  # noqa: E501
        header=headers[lang.upper()], body=body_templates[lang.upper()], logo=logo
    )

    msg.attach_alternative(html, "text/html")

    return msg


def custom_mailer_error_handler(connection, message, exc):
    combined_message = f"Error: {exc} Message: {message}"
    logger.warning(message, exc_info=exc)
    audit_log._commit_to_audit_log(mail_to="Unknown", action=combined_message)

    # call main handler since we just want to log stuff here
    return engine.handle_delivery_exception(connection, message, exc)
