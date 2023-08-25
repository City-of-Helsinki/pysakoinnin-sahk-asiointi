from django.test import TestCase
from mail_service.utils import extend_due_date_mail_constructor, mail_constructor, headers, events

mail_to = "test@email.com"

class TestMailUtils(TestCase):

    def test_extend_due_date_mail_constructor(self):
        new_due_date = "2023-01-01T00:30:00"

        # test that passed information can be found in mail
        mail = extend_due_date_mail_constructor(lang="FI", new_due_date=new_due_date, mail_to=mail_to)
        assert mail.subject == headers["FI"]
        assert mail.body == "<p>Eräpäivää siirretty, uusi eräpäivä on 01.01.2023"
        assert mail.to[0] == mail_to

        # check different languages
        mail = extend_due_date_mail_constructor(lang="EN", new_due_date=new_due_date, mail_to=mail_to)
        assert mail.subject == headers["EN"]

        mail = extend_due_date_mail_constructor(lang="SV", new_due_date=new_due_date, mail_to=mail_to)
        assert mail.subject == headers["SV"]

        # incorrect lang, default to FI
        mail = extend_due_date_mail_constructor(lang="INCORRECT_LANG", new_due_date=new_due_date, mail_to=mail_to)
        assert mail.subject == headers["FI"]

    def test_mail_constructor(self):
        # test that passed information can be found in mail
        mail = mail_constructor(event="received", lang="FI", mail_to=mail_to)
        assert mail.subject == headers["FI"]
        assert events["received"]["FI"] in mail.body
        assert mail.to[0] == mail_to

        # check different languages
        mail = mail_constructor(event="received", lang="EN", mail_to=mail_to)
        assert mail.subject == headers["EN"]

        mail = mail_constructor(event="received", lang="SV", mail_to=mail_to)
        assert mail.subject == headers["SV"]

        # incorrect lang, default to FI
        mail = mail_constructor(event="received", lang="INCORRECT_LANG", mail_to=mail_to)
        assert mail.subject == headers["FI"]

        
    
       


    
        
