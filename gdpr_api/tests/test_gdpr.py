import uuid
from unittest import mock

import pytest
import requests_mock
from django.conf import settings
from django.urls import reverse

from gdpr_api.tests.conftest import get_api_token_for_user_with_scopes
from pysakoinnin_sahk_asiointi.models import User


def _gdpr_action(method, scope, user, query_uuid=None):
    if not query_uuid:
        query_uuid = user.uuid
    with requests_mock.Mocker() as req_mock:
        gdpr_profile_url = reverse(
            "api-1.0.0:get_user_info", kwargs={"user_id": query_uuid}
        )
        auth_header = get_api_token_for_user_with_scopes(user.uuid, [scope], req_mock)
        return method(gdpr_profile_url, headers={"Authorization": auth_header})


def _gdpr_query(api_client, user, query_uuid=None):
    return _gdpr_action(api_client.get, settings.GDPR_API_QUERY_SCOPE, user, query_uuid)


def _gdpr_delete(api_client, user, query_uuid=None):
    return _gdpr_action(
        api_client.delete, settings.GDPR_API_DELETE_SCOPE, user, query_uuid
    )


@pytest.fixture
def user():
    return User(uuid=uuid.uuid4())


@pytest.mark.django_db
def test_gdpr_query_wrong_user(client, user):
    assert _gdpr_query(client, user, uuid.uuid4()).status_code == 403


@pytest.mark.django_db
def test_gdpr_query_user_with_no_documents(client, user):
    with mock.patch("api.views.ATVHandler.get_documents") as get_documents_mock:
        get_documents_mock.return_value = {"results": []}
        assert _gdpr_query(client, user).status_code == 204


@pytest.mark.django_db
def test_gdpr_query_user_with_documents(client, user):
    with mock.patch("api.views.ATVHandler.get_documents") as get_documents_mock:
        get_documents_mock.return_value = {
            "results": [
                {
                    "content": {
                        "object": {"key1": "value1"},
                        "list": [{"key2": "value2"}],
                        "key3": "value3",
                    }
                }
            ]
        }
        response = _gdpr_query(client, user)
        assert response.status_code == 200
        assert response.json() == {
            "children": [
                {
                    "children": [
                        {
                            "children": [{"key": "key1", "value": "value1"}],
                            "key": "object",
                        },
                        {
                            "children": [{"key": "key2", "value": "value2"}],
                            "key": "list",
                        },
                        {"key": "key3", "value": "value3"},
                    ],
                    "key": "CONTENT",
                }
            ],
            "key": "RESULTS",
        }


@pytest.mark.django_db
def test_gdpr_delete_wrong_user(client, user):
    assert _gdpr_delete(client, user, uuid.uuid4()).status_code == 403


@pytest.mark.django_db
def test_gdpr_delete_user_with_no_documents(client, user):
    with mock.patch("api.views.ATVHandler.get_documents") as get_documents_mock:
        get_documents_mock.return_value = {"results": []}
        assert _gdpr_delete(client, user).status_code == 204


@pytest.mark.django_db
def test_gdpr_delete_user_with_documents(client, user):
    with mock.patch("api.views.ATVHandler.get_documents") as get_documents_mock:
        get_documents_mock.return_value = {"results": [{}]}
        assert _gdpr_delete(client, user).status_code == 403


@pytest.mark.django_db
def test_gdpr_delete_with_query_scope(client, user):
    assert (
        _gdpr_action(client.delete, settings.GDPR_API_QUERY_SCOPE, user).status_code
        == 403
    )


@pytest.mark.django_db
def test_gdpr_query_with_delete_scope(client, user):
    assert (
        _gdpr_action(client.get, settings.GDPR_API_DELETE_SCOPE, user).status_code
        == 403
    )
