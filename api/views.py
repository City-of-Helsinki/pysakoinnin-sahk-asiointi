import json

from environ import Env
from ninja.errors import HttpError
from requests import request

from api.schemas import Objection, DocumentStatusRequest

env = Env()

BASE_DETAILS = {"username": "string",
                "password": "string",
                "customerID": {
                    "id": "string",
                    "type": 0
                },
                "customerLanguage": 0,
                "customerIPAddress": "string",
                }


class ATVHandler:
    @staticmethod
    def get_documents(user_id: str):
        try:
            req = request("GET", url=f"{env('ATV_ENDPOINT')}?user_id={user_id}",
                          headers={"x-api-key": env('ATV_API_KEY')})
            response_json = req.json()
            if len(response_json['results']) <= 0:
                raise HttpError(404, message="Resource not found")
            return response_json
        except HttpError as error:
            raise error

    @staticmethod
    def get_document_by_transaction_id(foul_id):
        try:
            req = request("GET", url=f"{env('ATV_ENDPOINT')}?transaction_id={foul_id}",
                          headers={"x-api-key": env('ATV_API_KEY')})
            response_json = req.json()
            if len(response_json["results"]) <= 0:
                raise HttpError(404, message="Resource not found")
            return response_json
        except HttpError as error:
            raise error

    @staticmethod
    def add_document(objection: Objection, foul_id: str):
        try:
            req = request('POST', f"{env('ATV_ENDPOINT')}",
                          headers={"x-api-key": env('ATV_API_KEY')}, data={
                    "draft": False,
                    "transaction_id": f"{foul_id}",
                    "tos_record_id": 12345,
                    "tos_function_id": 12345,
                    "content": json.dumps({**Objection.dict(objection)})},
                          files={'attachments': None})
            return req.json()
        except Exception as error:
            raise HttpError(500, message=str(error))


class PASIHandler:

    @staticmethod
    def get_foul_data(foul_number, register_number):
        try:
            req = request("POST", url=f"{env('PASI_ENDPOINT')}/api/v1/fouls/GetFoulData",
                          verify=False,
                          headers={'content-type': 'application/json', 'x-api-version': '1.0'},
                          json={
                              **BASE_DETAILS,
                              "foulNumber": foul_number,
                              "registerNumber": f"{register_number}"
                          })
            return req
        except Exception as error:
            raise HttpError(500, message=str(error))

    @staticmethod
    def get_transfer_data(transfer_number: int, register_number: str):
        try:
            req = request("POST", url=f"{env('PASI_ENDPOINT')}/api/v1/Transfers/GetTransferData",
                          verify=False,
                          headers={'content-type': 'application/json', 'x-api-version': '1.0'},
                          json={
                              **BASE_DETAILS,
                              "transferReferenceNumber": transfer_number,
                              "registerNumber": f"{register_number}"
                          })
            return req
        except Exception as error:
            raise HttpError(500, message=str(error))

    @staticmethod
    def extend_foul_due_date(foul_data):
        try:
            req = request("POST", url=f"{env('PASI_ENDPOINT')}/api/v1/fouls/ExtendFoulDueDate",
                          verify=False,
                          headers={'content-type': 'application/json', 'x-api-version': '1.0'},
                          json={
                              **BASE_DETAILS,
                              "foulNumber": foul_data.foul_number,
                              "registerNumber": f"{foul_data.register_number}"
                          })
            return req
        except Exception as error:
            raise HttpError(500, message=str(error))

    @staticmethod
    def save_objection(objection: Objection):
        try:
            req = request("POST", url=f"{env('PASI_ENDPOINT')}/api/v1/Objections/SaveObjection",
                          verify=False,
                          headers={'content-type': 'application/json', 'x-api-version': '1.0'},
                          json={**BASE_DETAILS, **Objection.dict(objection)}
                          )
            return req
        except Exception as error:
            raise HttpError(500, message=str(error))


class DocumentHandler:

    @staticmethod
    def set_document_status(status_request: DocumentStatusRequest):
        print(status_request)
