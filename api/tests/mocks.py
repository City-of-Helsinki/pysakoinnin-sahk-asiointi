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
            "additionalInfo": "12 metriä"
        },
        {
            "description": "Pysäköinti kiinteistölle johtavan ajotien kohdalle / siten, että ajoneuvoliikenne kiinteistölle tai sieltä pois on oleellisesti vaikeutunut. TLL 38 § 1 mom",
            "additionalInfo": "moikkaa "
        },
        {
            "description": "Pysäköinti/Pysäyttäminen pysäkkialueelle. TLL 3 § 1 mom.,  75 §, Liikennemerkki E6",
            "additionalInfo": "Ajoratamaalauksesta n. 2,0 m"
        }
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
    "responseCode": 0
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
    "responseCode": 0
}

MOCK_DUEDATE = {
    "responseCode": 0,
    "success": True,
    "errorcode": 0,
    "internalErrorDescription": "string",
    "dueDate": "2023-03-16T10:09:57.506Z",
    "dueDateExtendableReason": 0
}

MOCK_DUEDATE_REQUEST = {
    "foul_number": 113148427,
    "register_number": "HKR-999"
}


class MockResponse:
    def __init__(self, status_code, json_data):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data
