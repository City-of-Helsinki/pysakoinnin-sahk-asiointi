from unittest.mock import patch
from django.test import TestCase
from api.tests.mocks import MockResponse, MOCK_FOUL ,MOCK_TRANSFER, MOCK_ATV_DOCUMENT_RESPONSE

API_ROOT = "/api/v1"
class TestEndpoints(TestCase):
    # Purpose of these unauht tests is to ensure unauthorized users are not accessing endpoints
    # and developers using auth=None while locally developing are not accidentally pushing those into live
    @patch('api.views.PASIHandler.get_foul_data')
    def test_get_foul_data_unauth(self, get_foul_data_mock):
        get_foul_data_mock.return_value = MockResponse(200, MOCK_FOUL)
        response = self.client.get(f"{API_ROOT}/getFoulData")
        assert response.status_code == 401

    @patch('api.views.PASIHandler.get_transfer_data')
    def test_get_transfer_data_unauth(self, get_transfer_data_mock):
        get_transfer_data_mock.return_value = MockResponse(200, MOCK_TRANSFER)
        response = self.client.get(f"{API_ROOT}/getTransferData")
        assert response.status_code == 401
    
    @patch('api.views.ATVHandler.get_document_by_transaction_id')
    def test_get_document_by_transaction_id_unauth(self, get_document_by_transaction_id_mock):
        get_document_by_transaction_id_mock.return_value = MockResponse(200, MOCK_ATV_DOCUMENT_RESPONSE)
        response = self.client.get(f"{API_ROOT}/getDocumentByTransactionId/12345")
        assert response.status_code == 401