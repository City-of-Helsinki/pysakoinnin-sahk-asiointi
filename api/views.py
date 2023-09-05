import copy
import json

from django.http import HttpResponse
from environ import Env
from ninja.errors import HttpError
from requests import request

from api.schemas import DocumentStatusRequest, Objection
from pysakoinnin_sahk_asiointi.utils import stringToBool

env = Env()

# Env variable comes as a string, and the auto convert seems not to work thus manually convert values to bool
VALIDATE_PASI_CERTIFICATION = stringToBool(strBool=env('VALIDATE_PASI_CERTIFICATION'), default=True)

LANGUAGES = {
    "fi": 0,
    "sv": 1,
    "en": 2
}

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
            req = request("GET", url=f"{env('ATV_ENDPOINT')}?user_id={user_id}&page_size=999",
                          headers={"x-api-key": env('ATV_API_KEY')})
            response_json = req.json()
            if hasattr(response_json, 'results') and len(response_json['results']) <= 0:
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
    def add_document(content: dict, document_id, user_id: str, metadata: dict):
        try:
            req = request('POST', f"{env('ATV_ENDPOINT')}",
                          headers={"x-api-key": env('ATV_API_KEY')}, data={
                    "user_id": user_id,
                    "draft": False,
                    "deletable": False,
                    "transaction_id": f"{str(document_id)}",
                    "tos_record_id": 12345,
                    "tos_function_id": 12345,
                    "status": "sent",
                    "metadata": json.dumps(metadata),
                    "content": json.dumps(content)},
                          files={'attachments': None})
            return req
        except Exception as error:
            raise HttpError(500, message=str(error))


class PASIHandler:

    @staticmethod
    def get_foul_data(foul_number, register_number):
        try:
            req = request("POST", url=f"{env('PASI_ENDPOINT')}/api/v1/fouls/GetFoulData",
                          verify=VALIDATE_PASI_CERTIFICATION,
                          headers={'authorization': f"Basic {env('PASI_AUTH_KEY')}",
                                   'content-type': 'application/json',
                                   'x-api-version': '1.0'},
                          json={
                              **BASE_DETAILS,
                              "foulNumber": foul_number,
                              "registerNumber": f"{register_number}"
                          })
            if req.status_code == 404:
                raise HttpError(404, message="Resource not found")
            return req
        except HttpError as error:
            raise error
        except Exception as error:
            raise HttpError(500, message=str(error))

    @staticmethod
    def get_transfer_data(transfer_number: int, register_number: str):
        try:
            req = request("POST", url=f"{env('PASI_ENDPOINT')}/api/v1/Transfers/GetTransferData",
                          verify=VALIDATE_PASI_CERTIFICATION,
                          headers={'authorization': f"Basic {env('PASI_AUTH_KEY')}",
                                   'content-type': 'application/json',
                                   'x-api-version': '1.0'},
                          json={
                              **BASE_DETAILS,
                              "transferReferenceNumber": transfer_number,
                              "registerNumber": f"{register_number}"
                          })
            if req.status_code == 404:
                raise HttpError(404, message="Resource not found")
            return req
        except HttpError as error:
            raise error
        except Exception as error:
            raise HttpError(500, message=str(error))

    @staticmethod
    def extend_foul_due_date(foul_data):
        try:
            req = request("POST", url=f"{env('PASI_ENDPOINT')}/api/v1/fouls/ExtendFoulDueDate",
                          verify=VALIDATE_PASI_CERTIFICATION,
                          headers={'authorization': f"Basic {env('PASI_AUTH_KEY')}",
                                   'content-type': 'application/json',
                                   'x-api-version': '1.0',
                                   'Connection': 'keep-alive'},
                          json={
                              **BASE_DETAILS,
                              "foulNumber": foul_data.foul_number,
                              "registerNumber": f"{foul_data.register_number}"
                          })

            if req.status_code == 400:
                raise HttpError(400, message="Due date not extendable")

        except HttpError as error:
            raise error
        except Exception as error:
            raise HttpError(500, message=str(error))

        return req

    @staticmethod
    def save_objection(objection: Objection, objection_id):
        sanitised_objection = copy.deepcopy(objection)
        metadataLang = sanitised_objection.metadata.get('lang')
        customerLanguage = BASE_DETAILS["customerLanguage"]

        if metadataLang != None:
            if metadataLang in LANGUAGES:
                customerLanguage = LANGUAGES[metadataLang]
            else:
                raise ValueError("Unsupported language: " + metadataLang)

        del sanitised_objection.metadata

        try:
            req = request("POST", url=f"{env('PASI_ENDPOINT')}/api/v1/Objections/SaveObjection",
                          verify=VALIDATE_PASI_CERTIFICATION,
                          headers={'authorization': f"Basic {env('PASI_AUTH_KEY')}",
                                   'content-type': 'application/json',
                                   'x-api-version': '1.0'},
                          json={
                                **BASE_DETAILS,
                                **Objection.dict(sanitised_objection),
                                "customerLanguage": customerLanguage
                                }
                          )
            if req.status_code == 422:
                raise HttpError(422, message=req.json())

        except HttpError as error:
            raise error
        except Exception as error:
            raise HttpError(500, message=str(error))

        return req

class DocumentHandler:

    @staticmethod
    def set_document_status(document_id: str, status_request: DocumentStatusRequest):
        try:
            req = request('PATCH', f"{env('ATV_ENDPOINT')}{document_id}/",
                          headers={"x-api-key": env('ATV_API_KEY'),
                                   "accept": "application/json"},
                          data={"status": status_request.status.value},
                          files={"attachments": None})

            response_json = req.json()
            if "id" not in response_json:
                raise HttpError(404, message="Resource not found")
            return HttpResponse(200, 'OK')
        except HttpError as error:
            return error
