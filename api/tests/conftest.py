import uuid

import pytest
from django.test import Client

from pysakoinnin_sahk_asiointi.models import User


@pytest.fixture
def api_client():
    return Client()


@pytest.fixture
def user():
    return User.objects.create(uuid=uuid.uuid4())


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_login(user)
    return api_client


@pytest.fixture
def valid_foul_data_response():
    """Valid mock response data for FoulDataResponse schema."""
    return {
        "foulNumber": 12345,
        "foulDate": "2024-01-01",
        "monitoringStart": "2024-01-01T10:00:00",
        "registerNumber": "ABC-123",
        "vehicleType": "Car",
        "vehicleBrand": "Toyota",
        "vehicleColor": "Red",
        "address": "Test Street 1",
        "addressAdditionalInfo": "",
        "x_Coordinate": "60.1699",
        "y_Coordinate": "24.9384",
        "description": "Parking violation",
        "fouls": [{"description": "No parking", "additionalInfo": None}],
        "invoiceSumText": "80.00 EUR",
        "openAmountText": "80.00 EUR",
        "dueDate": "2024-02-01",
        "dueDateExtendable": True,
        "dueDateExtendableReason": 0,
        "responseCode": 0,
    }


@pytest.fixture
def valid_transfer_data_response():
    """Valid mock response data for TransferDataResponse schema."""
    return {
        "transferNumber": 67890,
        "transferDate": "2024-01-01",
        "registerNumber": "ABC-123",
        "vehicleType": "Car",
        "vehicleBrand": "Toyota",
        "vehicleColor": "Red",
        "startAddress": "Start Street 1",
        "startAddressAdditionalInfo": "",
        "endAddress": "End Street 1",
        "endAddressAdditionalInfo": "",
        "x_Coordinate": "60.1699",
        "y_Coordinate": "24.9384",
        "description": "Vehicle transfer",
        "fouls": [{"description": "Illegal parking", "additionalInfo": None}],
        "invoiceSumText": "200.00 EUR",
        "openAmountText": "200.00 EUR",
        "dueDate": "2024-02-01",
        "vehicleChassisNumber": "ABC123456789",
        "transferStartDate": "2024-01-01T10:00:00",
        "transferEndDate": "2024-01-01T12:00:00",
        "transferType": "1",
        "transferStatus": "1",
        "transferReason": "Illegal parking",
        "foulTypes": [1],
        "responseCode": 0,
    }


@pytest.fixture
def valid_objection_data():
    """Valid objection data for saveObjection endpoint."""
    return {
        "foulNumber": 12345,
        "ssn": "0",
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe@example.com",
        "mobilePhone": "+358401234567",
        "iban": "0",
        "authorRole": 1,
        "address": {
            "streetAddress": "Test Street 1",
            "postCode": "00100",
        },
        "description": "I object to this fine",
        "type": 0,
        "sendDecisionViaEService": True,
        "metadata": {},
    }
