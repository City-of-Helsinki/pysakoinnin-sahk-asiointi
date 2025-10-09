"""Pytest fixtures for API tests."""

import uuid

import pytest
from django.test import Client

from pysakoinnin_sahk_asiointi.models import User


@pytest.fixture
def api_client():
    return Client()


@pytest.fixture
def user():
    """Create a test user with a UUID."""
    return User.objects.create(uuid=uuid.uuid4())


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_login(user)
    return api_client
