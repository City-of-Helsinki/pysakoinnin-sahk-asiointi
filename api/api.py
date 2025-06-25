import copy
import logging

import ninja.errors
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from ninja import Router, Schema
from ninja.security import HttpBearer

from api.schemas import (
    ATVDocumentResponse,
    DocumentStatusRequest,
    ExtendDueDateResponse,
    FoulDataResponse,
    FoulRequest,
    Objection,
    TransferDataResponse,
)
from api.utils import virus_scan_attachment_file
from api.views import ATVHandler, DocumentHandler, PASIHandler
from suomifi_messages.connector import SuomiFIMessagesConnector
from suomifi_messages.utils import suomifi_message_constructor, extend_due_date_suomifi_message_constructor

router = Router()
sfm_logger = logging.getLogger("suomi-fi-messages")


class ApiKeyAuth(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str):
        if token == settings.PASI_API_KEY:
            return True


class NotFoundError(Schema):
    detail: str = "Resource not found"


@router.get(
    "/getFoulData", response={200: FoulDataResponse, 404: NotFoundError}, tags=["PASI"]
)
def get_foul_data(
    request, foul_number: int = 113148427, register_number: str = "HKR-999"
):
    """
    Retrieve foul data from PASI by foul number and register number
    """
    response = PASIHandler.get_foul_data(foul_number, register_number)

    return response.json()


@router.get(
    "/getTransferData",
    response={200: TransferDataResponse, 404: NotFoundError},
    tags=["PASI"],
)
def get_transfer_data(
    request, transfer_number: int = 11720143, register_number: str = "HKR-999"
):
    """
    Retrieve transfer data from PASI by transfer number and register number
    """
    response = PASIHandler.get_transfer_data(transfer_number, register_number)

    return response.json()


@router.post(
    "/extendDueDate",
    response={200: ExtendDueDateResponse, 400: None, 422: None},
    tags=["PASI"],
)
def extend_due_date(request, foul_data: FoulRequest):
    """
    Extend foul due date by 30 days
    """
    foul_data_for_pasi = copy.deepcopy(foul_data)
    del foul_data_for_pasi.metadata

    try:
        response = PASIHandler.extend_foul_due_date(foul_data_for_pasi)
    except Exception as error:
        raise ninja.errors.HttpError(500, message=str(error))

    response_json = response.json()

    ATVHandler.add_document(
        {**response_json}, foul_data.foul_number, request.user.uuid, metadata={}
    )

    sfm_connector = SuomiFIMessagesConnector()
    sfm_connector.login()

    title, body = extend_due_date_suomifi_message_constructor(
        new_due_date=response_json["dueDate"],
        lang=foul_data.metadata["lang"],
    )

    sfm_logger.debug("Sending extend due date message")
    sfm_response_json = sfm_connector.send_message(title, body)
    sfm_logger.debug(f"Extend due date message response: {sfm_response_json}")

    return response_json


@router.post(
    "/saveObjection", response={200: None, 204: None, 422: None}, tags=["PASI"]
)
def save_objection(request, objection: Objection):
    """
    Send a new objection to PASI
    """

    if hasattr(objection, "foulNumber") and objection.foulNumber is not None:
        objection_id = objection.foulNumber
    elif hasattr(objection, "transferNumber") and objection.transferNumber is not None:
        objection_id = objection.transferNumber
    else:
        raise ninja.errors.HttpError(
            422, message="Foul number or transfer number missing"
        )

    if objection.attachments is not None and len(objection.attachments) > 0:
        try:
            for attachment in objection.attachments:
                virus_scan_attachment_file(attachment.data)
        except ninja.errors.HttpError as error:
            raise error

    objection_without_attachment_data = copy.deepcopy(objection)
    for attachment in objection_without_attachment_data.attachments:
        del attachment.data

    try:
        ATVHandler.add_document(
            content=objection_without_attachment_data.dict(),
            document_id=objection_id,
            user_id=request.user.uuid,
            metadata={**objection.metadata},
        )
    except Exception as error:
        raise ninja.errors.HttpError(500, message=str(error))

    response = PASIHandler.save_objection(objection, objection_id)
    return response.status_code


@router.get("/getDocuments/", response={200: ATVDocumentResponse}, tags=["ATV"])
def get_atv_documents(request):
    """
    Retrieve all user documents from ATV with UUID
    """
    response = ATVHandler.get_documents(request.user.uuid)

    return response


@router.patch(
    "/setDocumentStatus",
    response={200: None, 401: None, 404: NotFoundError, 422: None},
    tags=["Pysaköinnin asiointi"],
    auth=ApiKeyAuth(),
)
def set_document_status(request, status_request: DocumentStatusRequest):
    """
    Update document status with ID and status
    """
    find_document_by_id = ATVHandler.get_document_by_transaction_id(status_request.id)
    document_id = find_document_by_id["results"][0]["id"]

    response = DocumentHandler.set_document_status(document_id, status_request)

    if response.status_code == 200:
        sfm_connector = SuomiFIMessagesConnector()
        sfm_connector.login()

        title, body = suomifi_message_constructor(
            event=status_request.status,
            lang=find_document_by_id["results"][0]["metadata"]["lang"],
        )

        sfm_logger.debug("Sending set document status message")
        sfm_response_json = sfm_connector.send_message(title, body)
        sfm_logger.debug(f"Set document status message response: {sfm_response_json}")

        return HttpResponse(200)
