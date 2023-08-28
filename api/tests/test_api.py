from unittest.mock import patch
from django.test import TestCase
from api.tests.mocks import MockResponse, MOCK_FOUL, MOCK_TRANSFER, MOCK_ATV_DOCUMENT_RESPONSE
from api.api import get_foul_data, get_transfer_data, get_atv_documents, get_document_by_transaction_id, save_objection
from ninja import Schema

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

    def to_dict(self):
        return {'lang': self.lang}

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
    metadata: Metadata = Metadata().dict()
    attachments: list = []

class TestApiFunctions(TestCase):

    @patch('api.views.PASIHandler.get_foul_data')
    def test_get_foul_data(self, get_foul_data_mock):
        get_foul_data_mock.return_value = MockResponse(200, MOCK_FOUL)
        result = get_foul_data(request=None, foul_number=MOCK_FOUL["foulNumber"], register_number=MOCK_FOUL["registerNumber"])
        assert result == MOCK_FOUL

    @patch('api.views.PASIHandler.get_transfer_data')
    def test_get_transfer_data(self, get_transfer_data_mock):
        get_transfer_data_mock.return_value = MockResponse(200, MOCK_TRANSFER)
        result = get_transfer_data(request=None, transfer_number=MOCK_TRANSFER["transferNumber"], register_number=MOCK_TRANSFER["registerNumber"])
        assert result == MOCK_TRANSFER
    
    @patch('api.views.ATVHandler.get_documents')
    def test_get_atv_documents(self, get_documents_mock):
        get_documents_mock.return_value = MockResponse(200, MOCK_ATV_DOCUMENT_RESPONSE)
        request =  Request(user=User("fakeid"))
        result = get_atv_documents(request=request)
        assert result.json() == MOCK_ATV_DOCUMENT_RESPONSE
    
    @patch('api.views.ATVHandler.get_document_by_transaction_id')
    def test_get_document_by_transaction_id(self, get_document_by_transaction_id_mock):
        get_document_by_transaction_id_mock.return_value = MockResponse(200, MOCK_ATV_DOCUMENT_RESPONSE)
        randomId = 12345 
        result = get_document_by_transaction_id(request=None, id=randomId)
        assert result.json() == MOCK_ATV_DOCUMENT_RESPONSE
    
    @patch('api.views.ATVHandler.add_document')
    @patch('api.views.PASIHandler.save_objection')
    def test_save_objection(self, save_objection_mock, add_document_mock):
        # status code is only interesting value here
        add_document_mock.return_value = MockResponse(200, {})
        save_objection_mock.return_value = MockResponse(200, {})

        objection = Objection()
        request =  Request(user=User("fakeid"))
        result = save_objection(request=request, objection=objection)

        assert result == 200
