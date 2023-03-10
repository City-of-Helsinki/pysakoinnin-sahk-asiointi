from django.test import TestCase
from ninja import NinjaAPI
from ninja.testing import TestClient

API_ROOT = "/api/v1/"

api = NinjaAPI()


class BasicTestCase(TestCase):
    def setup(self):
        self.client = TestClient(router_or_app=api)

    def test_basic(self):
        response = self.client.get(f"{API_ROOT}helloworld")
        assert response.status_code == 200
        assert response.json() == {"msg": "Hello world"}
