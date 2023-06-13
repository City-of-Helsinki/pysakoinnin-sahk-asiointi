import datetime
from zoneinfo import ZoneInfo

from anymail.message import attach_inline_image_file
from django.core.mail import EmailMultiAlternatives

headers = {
    'FI': 'Uusi tapahtuma Pysäköinnin Asioinnissa',
    'SV': 'Nya händelser i parkering e-tjänsten',
    'EN': 'New event in Parking e-service'
}

events = {
    'received': {
        'FI': 'Vastaanotettu',
        'SV': 'Mottaget',
        'EN': 'Received'
    },
    'handling': {
        'FI': 'Käsittelyssä',
        'SV': 'Bearbetning',
        'EN': 'In process'
    },
    'resolvedViaEService': {
        'FI': 'Päätös asioinnissa',
        'SV': 'Beslut i e-tjänster',
        'EN': 'Decision in e-services'
    },
    'resolvedViaMail': {
        'FI': 'Päätös postitettu',
        'SV': 'Beslutsbrev postat',
        'EN': 'Decision has been mailed'
    }
}


def mail_constructor(event: str, lang: str, mail_to: str):
    now = datetime.datetime.now(tz=ZoneInfo('Europe/Helsinki'))
    formatted_time = datetime.datetime.strftime(now, '%H:%M')
    if lang is None:
        lang = 'FI'

    bodyTemplates = {
        'FI': """<p>Pysäköinnin asiointiin on saapunut uusi tapahtuma: <i>{event}</i> klo {now}.
                <br>
                Kirjaudu pysäköinnin sähköiseen asiointiin https://pysakoinninasiointi.hel.fi
                <br>
                <br>
                (Tämä on automaattinen viesti jonka on lähettänyt Helsingin kaupungin pysäköinninvalvonnan sähköinen
                asiointipalvelu. Älä vastaa tähän viestiin.)</p>""".format(event=events[event][lang.upper()],
                                                                           now=formatted_time),

        'SV': """<p>Nya händelser har kommit in i parkering e-tjänsten: <i>{event}</i> på {now}.
                <br>
                Logga in på parkerings e-tjänster https://pysakoinninasiointi.hel.fi
                <br>
                <br>
                (Detta är ett automatiskt meddelande som skickas av Helsingfors stads parkeringsövervaknings e-tjänst. 
                Svara inte på detta meddelande.)</p>""".format(event=events[event][lang.upper()],
                                                               now=formatted_time),

        'EN': """<p>New event has arrived in the Parking e-service: <i>{event}</i> at {now}.
                    <br>
                    Sign in to parking e-services https://pysakoinninasiointi.hel.fi
                    <br>
                    <br>    
                (This is an automated message sent by the City of Helsinki parking control e-service. 
                Do not reply to this message.)</p>""".format(
            event=events[event][lang.upper()],
            now=formatted_time),
    }

    msg = EmailMultiAlternatives(
        headers[lang.upper()],
        bodyTemplates[lang.upper()],
        "Pysäköinnin Asiointi <noreply@hel.fi>",
        [mail_to], )

    logo = attach_inline_image_file(msg, 'mail_service/assets/logo.jpg')
    html = """
    <html>
    <body>
    <h2><img alt="Logo" src="cid:{logo}" height="24px" style="margin-right: 12px;"/>Pysäköinnin
        Asiointi</h2>
    <h1>{header}</h1>
    {body}
    </body>
    </html>""".format(header=headers[lang.upper()],
                      body=bodyTemplates[lang.upper()],
                      logo=logo)

    msg.attach_alternative(html, "text/html")

    return msg


def extend_due_date_mail_constructor(lang: str, new_due_date: str, mail_to):
    date = datetime.datetime.strptime(new_due_date, '%Y-%m-%dT%H:%M:%S')
    formatted_time = datetime.datetime.strftime(date, '%d.%m.%Y')

    if lang is None:
        lang = 'FI'

    bodyTemplates = {
        'FI': """<p>Eräpäivää siirretty, uusi eräpäivä on {new_due_date}""".format(new_due_date=formatted_time),

        'SV': """<p>Eräpäivää siirretty, uusi eräpäivä on {new_due_date}""".format(new_due_date=formatted_time),

        'EN': """<p>Eräpäivää siirretty, uusi eräpäivä on {new_due_date}""".format(new_due_date=formatted_time),
    }

    msg = EmailMultiAlternatives(
        headers[lang.upper()],
        bodyTemplates[lang.upper()],
        "Pysäköinnin Asiointi <noreply@hel.fi>",
        [mail_to], )

    logo = attach_inline_image_file(msg, 'mail_service/assets/logo.jpg')
    html = """
    <html>
    <body>
    <h2><img alt="Logo" src="cid:{logo}" height="24px" style="margin-right: 12px;"/>Pysäköinnin
        Asiointi</h2>
    <h1>{header}</h1>
    {body}
    </body>
    </html>""".format(header=headers[lang.upper()],
                      body=bodyTemplates[lang.upper()],
                      logo=logo)

    msg.attach_alternative(html, "text/html")

    return msg
