from django.test import TestCase
from mail_service.utils import extend_due_date_mail_constructor
from django.core.mail import EmailMultiAlternatives
from anymail.message import attach_inline_image_file
import datetime



lang = "FI"
body = "<p>Eräpäivää siirretty, uusi eräpäivä on 01.01.2023"
mail_to = "test@email.com"
new_due_date = "2023-01-01T00:30:00"
date = datetime.datetime.strptime(new_due_date, '%Y-%m-%dT%H:%M:%S')
formatted_time = datetime.datetime.strftime(date, '%d.%m.%Y')

mock_msg = EmailMultiAlternatives(
       "Uusi tapahtuma Pysäköinnin Asioinnissa",
        """<p>Eräpäivää siirretty, uusi eräpäivä on {new_due_date}""".format(new_due_date=formatted_time),
        "Pysäköinnin Asiointi <noreply@hel.fi>",
        [mail_to], )

logo = attach_inline_image_file(mock_msg, 'mail_service/assets/logo.jpg')
html = """
<html>
<body>
<h2><img alt="Logo" src="cid:{logo}" height="24px" style="margin-right: 12px;"/>Pysäköinnin
    Asiointi</h2>
<h1>{header}</h1>
{body}
</body>
</html>""".format(header='Uusi tapahtuma Pysäköinnin Asioinnissa',
                    body="""<p>Eräpäivää siirretty, uusi eräpäivä on {new_due_date}""".format(new_due_date=formatted_time),
                    logo=logo)

mock_msg.attach_alternative(html, "text/html")

class TestMailUtils(TestCase):

    def test_extend_due_date_mail_constructor(self):
        mail = extend_due_date_mail_constructor(lang=lang, new_due_date=new_due_date, mail_to=mail_to)
        assert mail.body == mock_msg.body
        assert mail.to[0] == mock_msg.to[0]
        assert mail.recipients() == mock_msg.recipients()
        assert mail.cc == mock_msg.cc
        assert mail.from_email == mock_msg.from_email
        assert mail.subject == mock_msg.subject
        assert mail.attachments.__sizeof__() == mock_msg.attachments.__sizeof__()
        assert True == False
        
