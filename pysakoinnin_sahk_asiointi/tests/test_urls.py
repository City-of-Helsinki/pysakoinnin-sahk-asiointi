import pytest


@pytest.mark.django_db
def test_health(client):
    response = client.get("/health/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_readiness(client):
    response = client.get("/readiness/")
    assert response.status_code == 200
