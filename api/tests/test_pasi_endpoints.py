from unittest.mock import patch

import ninja.errors
from django.test import TestCase
from ninja import NinjaAPI
from ninja.testing import TestClient

from api.tests.mocks import MockResponse, MOCK_FOUL, MOCK_TRANSFER

test_api = NinjaAPI()

API_ROOT = "/api/v1"


class TestPasiEndpoints(TestCase):

    def setup(self):
        self.client = TestClient(router_or_app=test_api)

    @patch('api.views.PASIHandler.get_foul_data')
    def test_get_foul_data(self, get_foul_data_mock):
        get_foul_data_mock.return_value = MockResponse(200, MOCK_FOUL)
        response = self.client.get(f"{API_ROOT}/getFoulData")
        assert response.status_code == 200
        assert response.json() == MOCK_FOUL

        get_foul_data_mock.side_effect = ninja.errors.HttpError(404, message="Resource not found")
        response = self.client.get(f"{API_ROOT}/getFoulData")
        assert response.status_code == 404

    @patch('api.views.PASIHandler.get_transfer_data')
    def test_get_transfer_data(self, get_transfer_data_mock):
        get_transfer_data_mock.return_value = MockResponse(200, MOCK_TRANSFER)
        response = self.client.get(f"{API_ROOT}/getTransferData")
        assert response.status_code == 200
        assert response.json() == MOCK_TRANSFER

        get_transfer_data_mock.side_effect = ninja.errors.HttpError(404, message="Resource not found")
        response = self.client.get(f"{API_ROOT}/getTransferData")
        assert response.status_code == 404
