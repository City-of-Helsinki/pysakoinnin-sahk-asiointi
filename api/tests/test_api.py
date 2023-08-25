from unittest.mock import patch
from django.test import TestCase
from api.tests.mocks import MockResponse, MOCK_FOUL, MOCK_TRANSFER, MOCK_ATV_DOCUMENT_RESPONSE
from api.api import get_foul_data, get_transfer_data, get_atv_documents

class User:
    def __init__(self, uuid):
        self.uuid = uuid
class Request:
    def __init__(self, user):
        self.user = user
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