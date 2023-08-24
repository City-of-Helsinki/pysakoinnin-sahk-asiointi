from django.test import TestCase
from mail_service.utils import extend_due_date_mail_constructor
from anymail.message import attach_inline_image_file


lang = "FI"
mail_to = "test@email.com"
new_due_date = "2023-01-01T00:30:00"

class TestMailUtils(TestCase):

    def test_extend_due_date_mail_constructor(self):
        mail = extend_due_date_mail_constructor(lang=lang, new_due_date=new_due_date, mail_to=mail_to)
        assert mail.subject == "Uusi tapahtuma Pysäköinnin Asioinnissa"
        assert mail.body == "<p>Eräpäivää siirretty, uusi eräpäivä on 01.01.2023"
        assert mail.to[0] == mail_to

        # check that language change works
        mail = extend_due_date_mail_constructor(lang="EN", new_due_date=new_due_date, mail_to=mail_to)
        assert mail.subject == 'New event in Parking e-service'

        mail = extend_due_date_mail_constructor(lang="SV", new_due_date=new_due_date, mail_to=mail_to)
        assert mail.subject == 'Nya händelser i parkering e-tjänsten'
        
