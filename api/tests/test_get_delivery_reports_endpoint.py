import pytest

from message_service.models import DeliveryReport


@pytest.fixture(autouse=True)
def setup_api_key(settings):
    settings.PASI_API_KEY = "test-key"


def auth_headers():
    return {"HTTP_AUTHORIZATION": "Bearer test-key"}


@pytest.mark.django_db
def test_get_delivery_reports_returns_all(client):
    DeliveryReport.objects.create(transaction_id="tx1")
    DeliveryReport.objects.create(transaction_id="tx2")

    response = client.get("/api/v1/getDeliveryReports", **auth_headers())

    assert response.status_code == 200
    assert len(response.json()["items"]) == 2


@pytest.mark.django_db
def test_get_delivery_reports_filter_by_transaction_id(client):
    DeliveryReport.objects.create(transaction_id="tx1")
    DeliveryReport.objects.create(transaction_id="tx2")

    response = client.get(
        "/api/v1/getDeliveryReports?transaction_id=tx1", **auth_headers()
    )

    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["transaction_id"] == "tx1"


@pytest.mark.django_db
def test_get_delivery_reports_filter_no_match(client):
    DeliveryReport.objects.create(transaction_id="tx1")

    response = client.get(
        "/api/v1/getDeliveryReports?transaction_id=nope", **auth_headers()
    )

    assert response.status_code == 200
    assert response.json()["items"] == []


@pytest.mark.django_db
def test_get_delivery_reports_response_shape(client):
    DeliveryReport.objects.create(transaction_id="tx1")

    response = client.get(
        "/api/v1/getDeliveryReports?transaction_id=tx1", **auth_headers()
    )

    assert response.status_code == 200
    item = response.json()["items"][0]
    assert set(item.keys()) == {
        "transaction_id",
        "suomifi_id",
        "created_at",
        "updated_at",
        "sent_at",
        "read_at",
        "status",
        "message_type",
    }


@pytest.mark.django_db
def test_get_delivery_reports_unauthorized(client):
    response = client.get("/api/v1/getDeliveryReports")

    assert response.status_code == 401
