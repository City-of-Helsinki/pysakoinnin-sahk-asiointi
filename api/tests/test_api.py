import json
from unittest.mock import MagicMock, patch

import pytest
from django.test import TestCase, override_settings
from django.urls import reverse
from ninja import Schema, errors

from api import api
from api.schemas import DocumentStatusEnum, DocumentStatusRequest
from api.tests.mocks import (
    MOCK_ATV_DOCUMENT_RESPONSE,
    MOCK_DUEDATE,
    MOCK_FOUL,
    MOCK_TRANSFER,
    MockResponse,
)

TEST_DOCUMENT_ID = "123"


# These classes are based on schemas defined in api.schemas
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
    email: str = "testing@email.com"


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
    metadata: dict = Metadata().dict()
    attachments: list = []


class FoulRequest(Schema):
    foul_number: int = 113148427
    register_number: str = "AB123"
    metadata: dict = Metadata()


class TestApiFunctions(TestCase):
    def setUp(self):
        self.user = User("fakeid")
        self.request = Request(user=self.user)

    @patch("api.views.PASIHandler.get_foul_data")
    def test_get_foul_data(self, get_foul_data_mock):
        get_foul_data_mock.return_value = MockResponse(200, MOCK_FOUL)

        result = api.get_foul_data(
            request=None,
            foul_number=MOCK_FOUL["foulNumber"],
            register_number=MOCK_FOUL["registerNumber"],
        )

        assert result == MOCK_FOUL

    @patch("api.views.PASIHandler.get_transfer_data")
    def test_get_transfer_data(self, get_transfer_data_mock):
        get_transfer_data_mock.return_value = MockResponse(200, MOCK_TRANSFER)

        result = api.get_transfer_data(
            request=None,
            transfer_number=MOCK_TRANSFER["transferNumber"],
            register_number=MOCK_TRANSFER["registerNumber"],
        )

        assert result == MOCK_TRANSFER

    @patch("api.views.ATVHandler.get_documents")
    def test_get_atv_documents(self, get_documents_mock):
        get_documents_mock.return_value = MockResponse(200, MOCK_ATV_DOCUMENT_RESPONSE)

        result = api.get_atv_documents(request=self.request)

        assert result.json() == MOCK_ATV_DOCUMENT_RESPONSE

    @patch("api.views.ATVHandler.add_document")
    @patch("api.views.PASIHandler.save_objection")
    def test_save_objection(self, save_objection_mock, add_document_mock):
        # status code is only interesting value here
        add_document_mock.return_value = MockResponse(200, {})
        save_objection_mock.return_value = MockResponse(200, {})

        objection = Objection()

        def save_obj():
            return api.save_objection(request=self.request, objection=objection)

        self.assertEqual(200, save_obj())

        # Raise httperror 422
        objection = Objection()
        objection.foulNumber = None
        objection.transferNumber = None
        self.assertRaises(errors.HttpError, save_obj)

        # Raise httperror 500
        objection = Objection()
        objection.metadata = "incorrect metadata"
        self.assertRaises(errors.HttpError, save_obj)

    @patch("api.views.ATVHandler.add_document")
    @patch("api.views.PASIHandler.extend_foul_due_date")
    def test_extend_due_date(self, extend_foul_due_date_mock, add_document_mock):
        add_document_mock.return_value = MockResponse(200, {})
        extend_foul_due_date_mock.return_value = MockResponse(200, MOCK_DUEDATE)

        foul_obj = FoulRequest()

        def extend():
            return api.extend_due_date(request=self.request, foul_data=foul_obj)

        response = extend()
        assert response == MOCK_DUEDATE

        foul_obj = FoulRequest()
        del foul_obj.foul_number
        self.assertRaises(AttributeError, extend)

        foul_obj = FoulRequest()
        extend_foul_due_date_mock.side_effect = errors.HttpError(500, "message")
        self.assertRaises(errors.HttpError, extend)


@pytest.mark.django_db
@patch("pysakoinnin_sahk_asiointi.urls.AuthBearer.authenticate")
@patch("api.views.ATVHandler.add_document")
@patch("api.views.PASIHandler.extend_foul_due_date")
def test_extend_due_date_email_validation_good_email(
    extend_foul_due_date_mock,
    add_document_mock,
    auth_mock,
    authenticated_client,
    user,
):
    add_document_mock.return_value = MockResponse(200, {})
    extend_foul_due_date_mock.return_value = MockResponse(200, MOCK_DUEDATE)
    auth_mock.return_value = MagicMock(user=user)

    data = FoulRequest().dict()
    data["metadata"]["email"] = "test@example.com"

    response = authenticated_client.post(
        "/api/v1/extendDueDate",
        data=json.dumps(data),
        content_type="application/json",
        HTTP_AUTHORIZATION="Bearer fake-token",
    )

    assert response.status_code == 200


@pytest.mark.django_db
@patch("pysakoinnin_sahk_asiointi.urls.AuthBearer.authenticate")
@patch("api.views.ATVHandler.add_document")
@patch("api.views.PASIHandler.extend_foul_due_date")
def test_extend_due_date_email_validation_bad_email(
    extend_foul_due_date_mock,
    add_document_mock,
    auth_mock,
    authenticated_client,
    user,
):
    add_document_mock.return_value = MockResponse(200, {})
    extend_foul_due_date_mock.return_value = MockResponse(200, MOCK_DUEDATE)
    auth_mock.return_value = MagicMock(user=user)

    data = FoulRequest().dict()
    data["metadata"]["email"] = "@example.com"

    response = authenticated_client.post(
        "/api/v1/extendDueDate",
        data=json.dumps(data),
        content_type="application/json",
        HTTP_AUTHORIZATION="Bearer fake-token",
    )

    assert response.status_code == 422


@pytest.mark.django_db
@patch("pysakoinnin_sahk_asiointi.urls.AuthBearer.authenticate")
@patch("api.views.ATVHandler.add_document")
@patch("api.views.PASIHandler.extend_foul_due_date")
def test_extend_due_date_email_validation_missing_email(
    extend_foul_due_date_mock,
    add_document_mock,
    auth_mock,
    authenticated_client,
    user,
):
    add_document_mock.return_value = MockResponse(200, {})
    extend_foul_due_date_mock.return_value = MockResponse(200, MOCK_DUEDATE)
    auth_mock.return_value = MagicMock(user=user)

    data = FoulRequest().dict()
    del data["metadata"]["email"]

    response = authenticated_client.post(
        "/api/v1/extendDueDate",
        data=json.dumps(data),
        content_type="application/json",
        HTTP_AUTHORIZATION="Bearer fake-token",
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "atv_get_response_status,atv_get_response_data,atv_patch_response_status,atv_patch_response_data,response_status,,email",
    [
        (200, {"results": []}, None, None, 404, False),
        (500, {}, None, None, 500, False),
        (
            200,
            {
                "results": [
                    {
                        "id": TEST_DOCUMENT_ID,
                        "metadata": {"lang": "fi"},
                        "content": {"email": "test@localhost"},
                    }
                ],
            },
            200,
            {
                "id": TEST_DOCUMENT_ID,
            },
            200,
            True,
        ),
    ],
)
@pytest.mark.django_db
@override_settings(DEBUG=False)
def test_set_document_status(
    client,
    requests_mock,
    settings,
    atv_get_response_status,
    atv_get_response_data,
    atv_patch_response_status,
    atv_patch_response_data,
    response_status,
    email,
    mailoutbox,
):
    settings.PASI_API_KEY = "pasi-api-key"
    settings.ATV_ENDPOINT = "http://atv/endpoint/"
    settings.MAILER_EMAIL_BACKEND = settings.EMAIL_BACKEND

    requests_mock.get(
        f"{settings.ATV_ENDPOINT}?transaction_id={TEST_DOCUMENT_ID}",
        status_code=atv_get_response_status,
        json=atv_get_response_data,
    )

    requests_mock.patch(
        f"{settings.ATV_ENDPOINT}{TEST_DOCUMENT_ID}/",
        status_code=atv_patch_response_status,
        json=atv_patch_response_data,
    )

    document_status_request = DocumentStatusRequest(
        id=TEST_DOCUMENT_ID, status=DocumentStatusEnum.received
    )

    client.raise_request_exception = False
    response = client.patch(
        reverse("api-1.0.0:set_document_status"),
        data=document_status_request.json(),
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Bearer {settings.PASI_API_KEY}",
    )

    assert response.status_code == response_status
    if email:
        assert len(mailoutbox) == 1
        expected_email = atv_get_response_data["results"][0]["content"]["email"]
        to_value = mailoutbox[0].to
        assert len(to_value) == 1
        assert expected_email == to_value[0]

    else:
        assert len(mailoutbox) == 0
