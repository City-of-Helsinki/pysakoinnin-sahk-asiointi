from unittest.mock import patch
from django.test import TestCase
from api.tests.mocks import (
    MockResponse,
    MOCK_FOUL,
    MOCK_TRANSFER,
    MOCK_ATV_DOCUMENT_RESPONSE,
    MOCK_DUEDATE,
)
from api import api
from ninja import Schema, errors


# These classes are based on schemas defined in api.schemas
class User:
    def __init__(self, uuid):
        self.uuid = uuid


class Request:
    def __init__(self, user):
        self.user = user


class Address(Schema):
    addressLine1: str = "string"
    addressLine2: str = "string"
    streetAddress: str = "string"
    postCode: str = "string"
    postOffice: str = "string"
    countryName: str = "string"


class Metadata(Schema):
    lang: str = "fi"
    email: str = "testing@email.com"


class Objection(Schema):
    foulNumber: int = 1
    transferNumber: int = 1
    folderID: str = "string"
    ssn: str = "string"
    firstName: str = "string"
    lastName: str = "string"
    email: str = "string"
    mobilePhone: str = "string"
    bic: str = "string"
    iban: str = "string"
    authorRole: int = 0
    address: Address = Address()
    description: str = "string"
    type: int = 0
    sendDecisionViaEService: bool = True
    metadata: dict = Metadata().dict()
    attachments: list = []


class FoulRequest(Schema):
    foul_number: str = "fi"
    register_number: str = "AB123"
    metadata: dict = Metadata().dict()


class TestApiFunctions(TestCase):
    def setUp(self):
        self.user = User("fakeid")
        self.request = Request(user=self.user)

    @patch("api.views.PASIHandler.get_foul_data")
    def test_get_foul_data(self, get_foul_data_mock):
        get_foul_data_mock.return_value = MockResponse(200, MOCK_FOUL)

        result = api.get_foul_data(
            request=None,
            foul_number=MOCK_FOUL["foulNumber"],
            register_number=MOCK_FOUL["registerNumber"],
        )

        assert result == MOCK_FOUL

    @patch("api.views.PASIHandler.get_transfer_data")
    def test_get_transfer_data(self, get_transfer_data_mock):
        get_transfer_data_mock.return_value = MockResponse(200, MOCK_TRANSFER)

        result = api.get_transfer_data(
            request=None,
            transfer_number=MOCK_TRANSFER["transferNumber"],
            register_number=MOCK_TRANSFER["registerNumber"],
        )

        assert result == MOCK_TRANSFER

    @patch("api.views.ATVHandler.get_documents")
    def test_get_atv_documents(self, get_documents_mock):
        get_documents_mock.return_value = MockResponse(200, MOCK_ATV_DOCUMENT_RESPONSE)

        result = api.get_atv_documents(request=self.request)

        assert result.json() == MOCK_ATV_DOCUMENT_RESPONSE

    @patch("api.views.ATVHandler.get_document_by_transaction_id")
    def test_get_document_by_transaction_id(self, get_document_by_transaction_id_mock):
        get_document_by_transaction_id_mock.return_value = MockResponse(
            200, MOCK_ATV_DOCUMENT_RESPONSE
        )

        randomId = 12345
        result = api.get_document_by_transaction_id(request=None, id=randomId)

        assert result.json() == MOCK_ATV_DOCUMENT_RESPONSE

    @patch("api.views.ATVHandler.add_document")
    @patch("api.views.PASIHandler.save_objection")
    def test_save_objection(self, save_objection_mock, add_document_mock):
        # status code is only interesting value here
        add_document_mock.return_value = MockResponse(200, {})
        save_objection_mock.return_value = MockResponse(200, {})

        objection = Objection()
        save_obj = lambda: api.save_objection(request=self.request, objection=objection)
        self.assertEqual(200, save_obj())

        # Raise httperror 422
        objection = Objection()
        objection.foulNumber = None
        objection.transferNumber = None
        self.assertRaises(errors.HttpError, save_obj)

        # Raise httperror 500
        objection = Objection()
        objection.metadata = "incorrect metadata"
        self.assertRaises(errors.HttpError, save_obj)

    @patch("api.views.ATVHandler.add_document")
    @patch("api.views.PASIHandler.extend_foul_due_date")
    def test_extend_due_date(self, extend_foul_due_date_mock, add_document_mock):
        add_document_mock.return_value = MockResponse(200, {})
        extend_foul_due_date_mock.return_value = MockResponse(200, MOCK_DUEDATE)

        foul_obj = FoulRequest()
        extend = lambda: api.extend_due_date(request=self.request, foul_data=foul_obj)

        # NOTE to enable this, sending emails needs to be mocked or skipped in test runs.
        # You could also use MAILER_EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend" in test runs
        # This was not issue in previous versions, but after email backend changes this became a problem

        # response = extend()
        # assert response == MOCK_DUEDATE

        foul_obj = FoulRequest()
        del foul_obj.foul_number
        self.assertRaises(AttributeError, extend)

        foul_obj = FoulRequest()
        extend_foul_due_date_mock.side_effect = errors.HttpError(500, "message")
        self.assertRaises(errors.HttpError, extend)
