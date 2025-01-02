import copy
import json
from datetime import date

import requests
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.http import HttpResponse
from ninja.errors import HttpError

from api.schemas import DocumentStatusRequest, Objection

LANGUAGES = {"fi": 0, "sv": 1, "en": 2}

BASE_DETAILS = {
    "username": "string",
    "password": "string",
    "customerID": {"id": "string", "type": 0},
    "customerLanguage": 0,
    "customerIPAddress": "string",
}


class ATVHandler:
    @staticmethod
    def get_documents(user_id: str):
        try:
            response = requests.get(
                f"{settings.ATV_ENDPOINT}?user_id={user_id}&page_size=999",
                headers={"x-api-key": settings.ATV_API_KEY},
                timeout=settings.REQUEST_TIMEOUT,
            )
            response_json = response.json()
            if hasattr(response_json, "results") and len(response_json["results"]) <= 0:
                raise HttpError(404, message="Resource not found")
            return response_json
        except HttpError as error:
            raise error

    @staticmethod
    def get_document_by_transaction_id(foul_id):
        try:
            response = requests.get(
                f"{settings.ATV_ENDPOINT}?transaction_id={foul_id}",
                headers={"x-api-key": settings.ATV_API_KEY},
                timeout=settings.REQUEST_TIMEOUT,
            )
            response_json = response.json()
            if len(response_json["results"]) <= 0:
                raise HttpError(404, message="Resource not found")
            return response_json
        except HttpError as error:
            raise error

    @staticmethod
    def add_document(content: dict, document_id, user_id: str, metadata: dict):
        delete_after = str(date.today() + relativedelta(years=2))

        try:
            response = requests.post(
                settings.ATV_ENDPOINT,
                headers={"x-api-key": settings.ATV_API_KEY},
                data={
                    "user_id": user_id,
                    "draft": False,
                    "deletable": False,
                    "delete_after": delete_after,
                    "transaction_id": f"{str(document_id)}",
                    "tos_record_id": 12345,
                    "tos_function_id": 12345,
                    "status": "sent",
                    "metadata": json.dumps(metadata),
                    "content": json.dumps(content),
                },
                files={"attachments": None},
                timeout=settings.REQUEST_TIMEOUT,
            )
            return response
        except Exception as error:
            raise HttpError(500, message=str(error))


class PASIHandler:
    @staticmethod
    def get_foul_data(foul_number, register_number):
        try:
            response = requests.post(
                f"{settings.PASI_ENDPOINT}/api/v1/fouls/GetFoulData",
                verify=settings.VALIDATE_PASI_CERTIFICATION,
                headers={
                    "authorization": f"Basic {settings.PASI_AUTH_KEY}",
                    "content-type": "application/json",
                    "x-api-version": "1.0",
                },
                json={
                    **BASE_DETAILS,
                    "foulNumber": foul_number,
                    "registerNumber": f"{register_number}",
                },
                timeout=settings.REQUEST_TIMEOUT,
            )
            if response.status_code == 404:
                raise HttpError(404, message="Resource not found")
            return response

        except HttpError as error:
            raise error
        except Exception as error:
            raise HttpError(500, message=str(error))

    @staticmethod
    def get_transfer_data(transfer_number: int, register_number: str):
        try:
            response = requests.post(
                f"{settings.PASI_ENDPOINT}/api/v1/Transfers/GetTransferData",
                verify=settings.VALIDATE_PASI_CERTIFICATION,
                headers={
                    "authorization": f"Basic {settings.PASI_AUTH_KEY}",
                    "content-type": "application/json",
                    "x-api-version": "1.0",
                },
                json={
                    **BASE_DETAILS,
                    "transferReferenceNumber": transfer_number,
                    "registerNumber": f"{register_number}",
                },
                timeout=settings.REQUEST_TIMEOUT,
            )
            if response.status_code == 404:
                raise HttpError(404, message="Resource not found")
            return response
        except HttpError as error:
            raise error
        except Exception as error:
            raise HttpError(500, message=str(error))

    @staticmethod
    def extend_foul_due_date(foul_data):
        try:
            response = requests.post(
                f"{settings.PASI_ENDPOINT}/api/v1/fouls/ExtendFoulDueDate",
                verify=settings.VALIDATE_PASI_CERTIFICATION,
                headers={
                    "authorization": f"Basic {settings.PASI_AUTH_KEY}",
                    "content-type": "application/json",
                    "x-api-version": "1.0",
                    "Connection": "keep-alive",
                },
                json={
                    **BASE_DETAILS,
                    "foulNumber": foul_data.foul_number,
                    "registerNumber": f"{foul_data.register_number}",
                },
                timeout=settings.REQUEST_TIMEOUT,
            )

            if response.status_code == 400:
                raise HttpError(400, message="Due date not extendable")

        except HttpError as error:
            raise error
        except Exception as error:
            raise HttpError(500, message=str(error))

        return response

    @staticmethod
    def save_objection(objection: Objection, objection_id):
        sanitised_objection = copy.deepcopy(objection)
        metadata_lang = sanitised_objection.metadata.get("lang")
        customer_language = BASE_DETAILS["customerLanguage"]

        if metadata_lang is not None:
            if metadata_lang in LANGUAGES:
                customer_language = LANGUAGES[metadata_lang]
            else:
                raise ValueError("Unsupported language: " + metadata_lang)

        del sanitised_objection.metadata

        try:
            response = requests.post(
                f"{settings.PASI_ENDPOINT}/api/v1/Objections/SaveObjection",
                verify=settings.VALIDATE_PASI_CERTIFICATION,
                headers={
                    "authorization": f"Basic {settings.PASI_AUTH_KEY}",
                    "content-type": "application/json",
                    "x-api-version": "1.0",
                },
                json={
                    **BASE_DETAILS,
                    **Objection.dict(sanitised_objection),
                    "customerLanguage": customer_language,
                },
                timeout=settings.REQUEST_TIMEOUT,
            )
            if response.status_code == 422:
                raise HttpError(422, message=response.json())

        except HttpError as error:
            raise error
        except Exception as error:
            raise HttpError(500, message=str(error))

        return response


class DocumentHandler:
    @staticmethod
    def set_document_status(document_id: str, status_request: DocumentStatusRequest):
        try:
            response = requests.patch(
                f"{settings.ATV_ENDPOINT}{document_id}/",
                headers={
                    "x-api-key": settings.ATV_API_KEY,
                    "accept": "application/json",
                },
                data={"status": status_request.status.value},
                files={"attachments": None},
                timeout=settings.REQUEST_TIMEOUT,
            )

            response_json = response.json()
            if "id" not in response_json:
                raise HttpError(404, message="Resource not found")
            return HttpResponse(200, "OK")
        except HttpError as error:
            return error
