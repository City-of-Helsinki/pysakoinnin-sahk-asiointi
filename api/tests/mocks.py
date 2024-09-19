MOCK_FOUL = {
    "foulNumber": 113148427,
    "foulDate": "2023-02-20T09:32:14.243",
    "monitoringStart": "2023-02-20T09:27:39.46",
    "registerNumber": "HKR-999",
    "vehicleType": "Henkilöauto M1",
    "vehicleModel": "CABRIOLET 2.3-89/255",
    "vehicleBrand": "Audi",
    "vehicleColor": "Keltainen",
    "address": "Bulevardi 15",
    "addressAdditionalInfo": "Vastapäätä",
    "x_Coordinate": "25496465",
    "y_Coordinate": "6672355",
    "description": "lunta maasssa",
    "fouls": [
        {
            "description": "Pysäköinti ajosuunnan vastaisesti taajaman ulkopuolella. TLL 36 § 2 mom",
            "additionalInfo": "12 metriä",
        },
        {
            "description": """Pysäköinti kiinteistölle johtavan ajotien kohdalle / siten,
                              että ajoneuvoliikenne kiinteistölle tai sieltä pois on oleellisesti
                              vaikeutunut. TLL 38 § 1 mom""",
            "additionalInfo": "moikkaa ",
        },
        {
            "description": "Pysäköinti/Pysäyttäminen pysäkkialueelle. TLL 3 § 1 mom.,  75 §, Liikennemerkki E6",
            "additionalInfo": "Ajoratamaalauksesta n. 2,0 m",
        },
    ],
    "invoiceSumText": "80,00 EUR",
    "openAmountText": "80,00 EUR",
    "dueDate": "2023-04-05T09:32:00",
    "referenceNumber": "113148427759",
    "iban": "FI9016603001198707",
    "barCode": "490166030011987070000800000000000000113148427759230405",
    "foulMakerAddress": None,
    "attachments": [],
    "dueDateExtendable": False,
    "dueDateExtendableReason": 4,
    "responseCode": 0,
}

MOCK_TRANSFER = {
    "transferNumber": 36136951,
    "transferDate": "2022-01-09T15:00:00",
    "registerNumber": "HKR-999",
    "vehicleType": "Henkilöauto M1",
    "vehicleModel": "CABRIOLET 2.3-89/255",
    "vehicleBrand": "Audi",
    "vehicleColor": "Keltainen",
    "startAddress": "Testi siirto",
    "startAddressAdditionalInfo": "",
    "endAddress": "Testi siirto",
    "endAddressAdditionalInfo": "",
    "x_Coordinate": "0",
    "y_Coordinate": "0",
    "description": "",
    "fouls": [],
    "invoiceSumText": "351,00 EUR",
    "openAmountText": "351,00 EUR",
    "dueDate": "2023-03-24T00:00:00",
    "referenceNumber": None,
    "iban": None,
    "barCode": "497800017009033300003510000000000727411720143753230324",
    "vehicleOwnerAddress": None,
    "attachments": [],
    "vehicleChassisNumber": "",
    "transferStartDate": "2022-01-09T15:00:00",
    "transferEndDate": "2022-01-09T15:05:00",
    "transferType": "Maksullinen lähisiirto",
    "transferStatus": "Suoritettu",
    "transferReason": "Katualue varattu",
    "foulTypes": [],
    "responseCode": 0,
}

MOCK_DUEDATE = {
    "success": True,
    "errorcode": "string",
    "internalErrorDescription": "string",
    "dueDate": "2023-04-05T09:32:00",
    "dueDateExtendableReason": 0,
    "responseCode": 0,
}

MOCK_DUEDATE_REQUEST = {"foul_number": 113148427, "register_number": "HKR-999"}

MOCK_ATV_DOCUMENT_RESPONSE = {
    "count": 1,
    "next": None,
    "previous": None,
    "results": [
        {
            "id": "4y11fb6c-8b25-4c3c-9ea5-e62b976667e1",
            "created_at": "2023-06-02T13:48:59.258113+03:00",
            "updated_at": "2023-08-03T17:38:49.303800+03:00",
            "status": {
                "value": "received",
                "status_display_values": {},
                "timestamp": "2023-06-02T13:54:20.738979+03:00",
                "activities": [],
            },
            "status_histories": [
                {
                    "value": "received",
                    "status_display_values": {},
                    "timestamp": "2023-06-02T13:54:20.738979+03:00",
                    "activities": [],
                },
                {
                    "value": "sent",
                    "status_display_values": {},
                    "timestamp": "2023-06-02T13:48:59.269477+03:00",
                    "activities": [],
                },
            ],
            "type": "",
            "human_readable_type": {},
            "service": "Pysäköinnin Sähköinen Asiointi",
            "user_id": "uuid",
            "transaction_id": "113148474",
            "business_id": "",
            "tos_function_id": "12345",
            "tos_record_id": "12345",
            "metadata": {"foulNumber": "113148474", "registerNumber": "hkr-999"},
            "content": {
                "foulNumber": 113148474,
                "transferNumber": None,
                "folderID": None,
                "ssn": "210281-9988",
                "firstName": "Nordea",
                "lastName": "Demo",
                "email": "test@gmail.fi",
                "mobilePhone": "+58254545414",
                "bic": None,
                "iban": "FI90 1345 1234 1234 12",
                "authorRole": 2,
                "address": {
                    "addressLine1": None,
                    "addressLine2": None,
                    "streetAddress": "katu 8",
                    "postCode": "00580",
                    "postOffice": "jhelksini",
                    "countryName": None,
                },
                "description": "description",
                "attachments": [],
                "type": 0,
                "sendDecisionViaEService": True,
                "metadata": {"foulNumber": "113148474", "registerNumber": "hkr-999"},
            },
            "draft": False,
            "locked_after": None,
            "deletable": False,
            "attachments": [],
        }
    ],
}


class MockResponse:
    def __init__(self, status_code, json_data):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data
