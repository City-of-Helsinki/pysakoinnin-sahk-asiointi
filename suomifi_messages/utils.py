import datetime
import logging
from typing import Tuple
from zoneinfo import ZoneInfo

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


def suomifi_message_constructor(event: str, lang: str) -> Tuple[str, str]:
    now = datetime.datetime.now(tz=ZoneInfo("Europe/Helsinki"))
    formatted_time = datetime.datetime.strftime(now, "%H:%M")
    if lang not in headers:
        lang = "FI"

    body_templates = {
        "FI": """Pysäköinnin asiointiin on saapunut uusi tapahtuma: {event} klo {now}.

Kirjaudu pysäköinnin sähköiseen asiointiin https://pysakoinninasiointi.hel.fi

(Tämä on automaattinen viesti jonka on lähettänyt Helsingin kaupungin pysäköinninvalvonnan sähköinen asiointipalvelu. Älä vastaa tähän viestiin.)""".format(
            event=events[event][lang.upper()], now=formatted_time
        ),
        "SV": """Nya händelser har kommit in i parkering e-tjänsten: {event} på {now}.

Logga in på parkerings e-tjänster https://pysakoinninasiointi.hel.fi

(Detta är ett automatiskt meddelande som skickas av Helsingfors stads parkeringsövervaknings e-tjänst. Svara inte på detta meddelande.)""".format(
            event=events[event][lang.upper()], now=formatted_time
        ),
        "EN": """New event has arrived in the Parking e-service: {event} at {now}.

Sign in to parking e-services https://pysakoinninasiointi.hel.fi

(This is an automated message sent by the City of Helsinki parking control e-service. Do not reply to this message.)""".format(
            event=events[event][lang.upper()], now=formatted_time
        ),
    }

    return headers[lang.upper()], body_templates[lang.upper()]


def extend_due_date_suomifi_message_constructor(
    lang: str, new_due_date: str
) -> Tuple[str, str]:
    date = datetime.datetime.strptime(new_due_date, "%Y-%m-%dT%H:%M:%S")
    formatted_time = datetime.datetime.strftime(date, "%d.%m.%Y")

    body_templates = {
        "FI": "Eräpäivää siirretty, uusi eräpäivä on {new_due_date}".format(
            new_due_date=formatted_time
        ),
        "SV": (
            "Förfallodagen har skjutits upp. Nytt förfallodag är {new_due_date}"
        ).format(new_due_date=formatted_time),
        "EN": (
            "The due date has been postponed. New due date is {new_due_date}"
        ).format(new_due_date=formatted_time),
    }
    if lang not in body_templates:
        lang = "FI"

    return headers[lang.upper()], body_templates[lang.upper()]
