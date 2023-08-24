from unittest.mock import patch
from django.test import TestCase
from api.tests.mocks import MockResponse, MOCK_FOUL, MOCK_TRANSFER
from api.api import get_foul_data, get_transfer_data


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

