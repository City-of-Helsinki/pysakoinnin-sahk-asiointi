import copy
import json

from environ import Env
from ninja.errors import HttpError
from requests import request

from api.schemas import DocumentStatusRequest, Objection

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
            req = request("GET", url=f"{env('ATV_ENDPOINT')}?user_id={user_id}&page_size=999",
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
    def add_document(content, document_id, user_id: str, metadata: dict):
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
                    "content": content.json()},
                          files={'attachments': None})
            return req
        except Exception as error:
            raise HttpError(500, message=str(error))


class PASIHandler:

    @staticmethod
    def get_foul_data(foul_number, register_number):
        try:
            req = request("POST", url=f"{env('PASI_ENDPOINT')}/api/v1/fouls/GetFoulData",
                          verify=False,
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
                          verify=False,
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
    def extend_foul_due_date(foul_data, user_id):
        try:
            req = request("POST", url=f"{env('PASI_ENDPOINT')}/api/v1/fouls/ExtendFoulDueDate",
                          verify=False,
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
            if hasattr(req, "json"):
                try:
                    ATVHandler.add_document(req, foul_data.foul_number, user_id, metadata={})
                    return req
                except Exception as error:
                    raise HttpError(500, message=str(error))

        except HttpError as error:
            raise error
        except Exception as error:
            raise HttpError(500, message=str(error))

    @staticmethod
    def save_objection(objection: Objection, objection_id, user_id):
        sanitised_objection = copy.deepcopy(objection)
        del sanitised_objection.metadata

        try:
            req = request("POST", url=f"{env('PASI_ENDPOINT')}/api/v1/Objections/SaveObjection",
                          verify=False,
                          headers={'authorization': f"Basic {env('PASI_AUTH_KEY')}",
                                   'content-type': 'application/json',
                                   'x-api-version': '1.0'},
                          json={**BASE_DETAILS, **Objection.dict(sanitised_objection)}
                          )
            if req.status_code == 422:
                raise HttpError(422, message=req.json())
            if req.status_code == 200 or req.status_code == 204:
                try:
                    ATVHandler.add_document(sanitised_objection, objection_id, user_id, metadata=objection.metadata)
                    return req
                except Exception as error:
                    raise HttpError(500, message=str(error))

        except HttpError as error:
            raise error
        except Exception as error:
            raise HttpError(500, message=str(error))


class DocumentHandler:

    @staticmethod
    def set_document_status(status_request: DocumentStatusRequest):
        find_document_by_id = ATVHandler.get_document_by_transaction_id(status_request.id)
        document_id = find_document_by_id["results"][0]['id']

        try:
            req = request('PATCH', f"{env('ATV_ENDPOINT')}{document_id}/",
                          headers={"x-api-key": env('ATV_API_KEY'),
                                   "accept": "application/json"},
                          data={"status": status_request.status.value},
                          files={"attachments": None})

            response_json = req.json()
            if hasattr(response_json, "id") is None:
                raise HttpError(404, message="Resource not found")
            return {200, "OK"}
        except HttpError as error:
            return error
