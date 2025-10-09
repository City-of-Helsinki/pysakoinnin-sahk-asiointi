"""
Tests for optional fields in schemas.
These tests serve as a safety net against breaking changes in Pydantic or Django Ninja,
verifying that optional field behavior remains consistent across library upgrades.
"""

from api.schemas import (
    AddressField,
    ATVDocumentResponse,
    ATVDocumentSchema,
    ExtendDueDateResponse,
    FoulDataResponse,
    FoulSchema,
    Objection,
    TransferDataResponse,
)


class TestATVDocumentSchemaOptionalFields:
    def test_atv_document_schema_all_optional_fields_present(self):
        data = {
            "id": "4y11fb6c-8b25-4c3c-9ea5-e62b976667e1",
            "created_at": "2023-06-02T13:48:59.258113+03:00",
            "updated_at": "2023-08-03T17:38:49.303800+03:00",
            "status": {"value": "sent"},
            "status_histories": [],
            "type": "objection",
            "human_readable_type": {"fi": "Oikaisuvaatimus"},
            "service": "Pysäköinnin Sähköinen Asiointi",
            "user_id": "uuid-1234-5678",
            "transaction_id": "113148474",
            "business_id": "business-123",
            "tos_function_id": "12345",
            "tos_record_id": "12345",
            "metadata": {"foulNumber": "113148474"},
            "content": {"description": "Test content"},
            "draft": False,
            "locked_after": "2024-01-01T00:00:00",
            "deletable": False,
            "delete_after": "2025-06-02T00:00:00",
            "attachments": [],
        }
        document = ATVDocumentSchema(**data)
        assert document.user_id == "uuid-1234-5678"
        assert document.locked_after == "2024-01-01T00:00:00"
        assert document.delete_after == "2025-06-02T00:00:00"

    def test_atv_document_schema_without_optional_fields(self):
        data = {
            "id": "4y11fb6c-8b25-4c3c-9ea5-e62b976667e1",
            "created_at": "2023-06-02T13:48:59.258113+03:00",
            "updated_at": "2023-08-03T17:38:49.303800+03:00",
            "status": {"value": "sent"},
            "status_histories": [],
            "type": "objection",
            "human_readable_type": {"fi": "Oikaisuvaatimus"},
            "service": "Pysäköinnin Sähköinen Asiointi",
            "transaction_id": "113148474",
            "business_id": "business-123",
            "tos_function_id": "12345",
            "tos_record_id": "12345",
            "metadata": {"foulNumber": "113148474"},
            "content": {"description": "Test content"},
            "draft": False,
            "deletable": False,
            "attachments": [],
        }
        document = ATVDocumentSchema(**data)
        assert document.user_id is None
        assert document.locked_after is None
        assert document.delete_after is None


class TestATVDocumentResponseOptionalFields:
    def test_atv_document_response_with_pagination(self):
        data = {
            "count": 100,
            "next": "https://api.example.com/documents?page=2",
            "previous": "https://api.example.com/documents?page=0",
            "results": [],
        }
        response = ATVDocumentResponse(**data)
        assert response.count == 100
        assert response.next == "https://api.example.com/documents?page=2"
        assert response.previous == "https://api.example.com/documents?page=0"

    def test_atv_document_response_without_pagination(self):
        data = {
            "count": 1,
            "results": [],
        }
        response = ATVDocumentResponse(**data)
        assert response.count == 1
        assert response.next is None
        assert response.previous is None


class TestFoulSchemaOptionalFields:
    def test_foul_schema_with_additional_info(self):
        data = {
            "description": "Parking violation",
            "additionalInfo": "Near the entrance",
        }
        foul = FoulSchema(**data)
        assert foul.description == "Parking violation"
        assert foul.additionalInfo == "Near the entrance"

    def test_foul_schema_without_additional_info(self):
        data = {"description": "Parking violation"}
        foul = FoulSchema(**data)
        assert foul.description == "Parking violation"
        assert foul.additionalInfo is None


class TestFoulDataResponseOptionalFields:
    def test_foul_data_response_all_optional_fields_present(self):
        data = {
            "foulNumber": 12345,
            "foulDate": "2023-01-01T00:00:00",
            "monitoringStart": "2023-01-01T00:00:00",
            "registerNumber": "ABC-123",
            "vehicleType": "Car",
            "vehicleModel": "Tesla Model 3",
            "vehicleBrand": "Tesla",
            "vehicleColor": "Red",
            "address": "Test Street 1",
            "addressAdditionalInfo": "Near park",
            "x_Coordinate": "123456",
            "y_Coordinate": "654321",
            "description": "Test description",
            "fouls": [],
            "invoiceSumText": "100 EUR",
            "openAmountText": "100 EUR",
            "dueDate": "2023-02-01T00:00:00",
            "referenceNumber": "REF123",
            "iban": "0",
            "barCode": "1234567890",
            "foulMakerAddress": "Maker Street 1",
            "attachments": [],
            "dueDateExtendable": True,
            "dueDateExtendableReason": 1,
            "responseCode": 0,
        }
        response = FoulDataResponse(**data)
        assert response.vehicleModel == "Tesla Model 3"
        assert response.referenceNumber == "REF123"
        assert response.iban == "0"
        assert response.barCode == "1234567890"
        assert response.foulMakerAddress == "Maker Street 1"

    def test_foul_data_response_without_optional_fields(self):
        data = {
            "foulNumber": 12345,
            "foulDate": "2023-01-01T00:00:00",
            "monitoringStart": "2023-01-01T00:00:00",
            "registerNumber": "ABC-123",
            "vehicleType": "Car",
            "vehicleBrand": "Tesla",
            "vehicleColor": "Red",
            "address": "Test Street 1",
            "addressAdditionalInfo": "Near park",
            "x_Coordinate": "123456",
            "y_Coordinate": "654321",
            "description": "Test description",
            "fouls": [],
            "invoiceSumText": "100 EUR",
            "openAmountText": "100 EUR",
            "dueDate": "2023-02-01T00:00:00",
            "dueDateExtendable": True,
            "dueDateExtendableReason": 1,
            "responseCode": 0,
        }
        response = FoulDataResponse(**data)
        assert response.vehicleModel is None
        assert response.referenceNumber is None
        assert response.iban is None
        assert response.barCode is None
        assert response.foulMakerAddress is None
        assert response.attachments == []  # Default factory


class TestExtendDueDateResponseOptionalFields:
    def test_extend_due_date_response_with_error_fields(self):
        data = {
            "success": False,
            "errorcode": "ERR_001",
            "internalErrorDescription": "Database connection failed",
            "dueDate": "2023-03-01T00:00:00",
            "dueDateExtendableReason": 2,
            "responseCode": 500,
        }
        response = ExtendDueDateResponse(**data)
        assert response.success is False
        assert response.errorcode == "ERR_001"
        assert response.internalErrorDescription == "Database connection failed"

    def test_extend_due_date_response_without_error_fields(self):
        data = {
            "success": True,
            "dueDate": "2023-03-01T00:00:00",
            "dueDateExtendableReason": 0,
            "responseCode": 200,
        }
        response = ExtendDueDateResponse(**data)
        assert response.success is True
        assert response.errorcode is None
        assert response.internalErrorDescription is None
        assert response.dueDate == "2023-03-01T00:00:00"


class TestAddressFieldOptionalFields:
    def test_address_field_all_fields_present(self):
        data = {
            "addressLine1": "Apartment 5B",
            "addressLine2": "Building C",
            "streetAddress": "Main Street 123",
            "postCode": "00100",
            "postOffice": "Helsinki",
            "countryName": "Finland",
        }
        address = AddressField(**data)
        assert address.addressLine1 == "Apartment 5B"
        assert address.addressLine2 == "Building C"
        assert address.streetAddress == "Main Street 123"
        assert address.postCode == "00100"
        assert address.postOffice == "Helsinki"
        assert address.countryName == "Finland"

    def test_address_field_only_required_fields(self):
        data = {
            "streetAddress": "Main Street 123",
            "postCode": "00100",
        }
        address = AddressField(**data)
        assert address.addressLine1 is None
        assert address.addressLine2 is None
        assert address.streetAddress == "Main Street 123"
        assert address.postCode == "00100"
        assert address.postOffice is None
        assert address.countryName is None


class TestObjectionOptionalFields:
    def test_objection_with_all_optional_fields(self):
        data = {
            "foulNumber": 12345,
            "transferNumber": 67890,
            "folderID": "FOLDER-123",
            "ssn": "0",
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "mobilePhone": "+358401234567",
            "bic": "NDEAFIHH",
            "iban": "0",
            "authorRole": 1,
            "address": {
                "addressLine1": "Apt 5",
                "streetAddress": "Test Street 1",
                "postCode": "00100",
                "postOffice": "Helsinki",
            },
            "description": "Full objection",
            "attachments": [
                {
                    "fileName": "document.pdf",
                    "mimeType": "application/pdf",
                    "data": "base64data",
                }
            ],
            "type": 0,
            "sendDecisionViaEService": True,
            "metadata": {"lang": "fi", "source": "web"},
        }
        objection = Objection(**data)
        assert objection.foulNumber == 12345
        assert objection.transferNumber == 67890
        assert objection.folderID == "FOLDER-123"
        assert objection.bic == "NDEAFIHH"
        assert objection.attachments is not None
        assert len(objection.attachments) == 1
        assert objection.attachments[0].fileName == "document.pdf"
        assert objection.metadata == {"lang": "fi", "source": "web"}

    def test_objection_without_optional_fields(self):
        data = {
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
            "description": "Minimal objection",
            "type": 0,
            "sendDecisionViaEService": True,
        }
        objection = Objection(**data)
        assert objection.foulNumber is None
        assert objection.transferNumber is None
        assert objection.folderID is None
        assert objection.bic is None
        assert objection.attachments is None
        assert objection.metadata is None


class TestTransferDataResponseOptionalFields:
    def test_transfer_data_response_all_optional_fields_present(self):
        data = {
            "transferNumber": 11720143,
            "transferDate": "2022-01-09T15:00:00",
            "registerNumber": "ABC-123",
            "vehicleType": "Henkilöauto M1",
            "vehicleModel": "CABRIOLET 2.3-89/255",
            "vehicleBrand": "Audi",
            "vehicleColor": "Keltainen",
            "startAddress": "Start Street 1",
            "startAddressAdditionalInfo": "Near station",
            "endAddress": "End Street 2",
            "endAddressAdditionalInfo": "Opposite mall",
            "x_Coordinate": "25496465",
            "y_Coordinate": "6672355",
            "description": "Transfer description",
            "fouls": [],
            "invoiceSumText": "351,00 EUR",
            "openAmountText": "351,00 EUR",
            "dueDate": "2023-03-24T00:00:00",
            "referenceNumber": "11720143753",
            "iban": "0",
            "barCode": "497800017009033300003510000000000727411720143753230324",
            "vehicleOwnerAddress": "Owner Street 5, 00100 Helsinki",
            "attachments": [],
            "vehicleChassisNumber": "VIN12345678901234",
            "transferStartDate": "2022-01-09T15:00:00",
            "transferEndDate": "2022-01-09T15:05:00",
            "transferType": "Maksullinen lähisiirto",
            "transferStatus": "Suoritettu",
            "transferReason": "Katualue varattu",
            "foulTypes": [],
            "responseCode": 0,
        }
        response = TransferDataResponse(**data)
        assert response.vehicleModel == "CABRIOLET 2.3-89/255"
        assert response.referenceNumber == "11720143753"
        assert response.iban == "0"
        assert (
            response.barCode == "497800017009033300003510000000000727411720143753230324"
        )
        assert response.vehicleOwnerAddress == "Owner Street 5, 00100 Helsinki"

    def test_transfer_data_response_without_optional_fields(self):
        data = {
            "transferNumber": 11720143,
            "transferDate": "2022-01-09T15:00:00",
            "registerNumber": "ABC-123",
            "vehicleType": "Henkilöauto M1",
            "vehicleBrand": "Audi",
            "vehicleColor": "Keltainen",
            "startAddress": "Start Street 1",
            "startAddressAdditionalInfo": "Near station",
            "endAddress": "End Street 2",
            "endAddressAdditionalInfo": "Opposite mall",
            "x_Coordinate": "25496465",
            "y_Coordinate": "6672355",
            "description": "Transfer description",
            "fouls": [],
            "invoiceSumText": "351,00 EUR",
            "openAmountText": "351,00 EUR",
            "dueDate": "2023-03-24T00:00:00",
            "vehicleChassisNumber": "VIN12345678901234",
            "transferStartDate": "2022-01-09T15:00:00",
            "transferEndDate": "2022-01-09T15:05:00",
            "transferType": "Maksullinen lähisiirto",
            "transferStatus": "Suoritettu",
            "transferReason": "Katualue varattu",
            "foulTypes": [],
            "responseCode": 0,
        }
        response = TransferDataResponse(**data)
        assert response.vehicleModel is None
        assert response.referenceNumber is None
        assert response.iban is None
        assert response.barCode is None
        assert response.vehicleOwnerAddress is None
        assert response.attachments == []
