from typing import Any

from ninja import Router, Schema
from ninja.errors import HttpError

from api.schemas import FoulDataResponse, ATVDocumentResponse, ExtendDueDateResponse, TransferDataResponse
from api.views import *

router = Router()


class FoulRequest(Schema):
    foul_number: int = 113148427
    register_number: str = "HKR-999"


@router.get("/helloworld")
def helloworld(request):
    return {"msg": 'Hello world'}


@router.get('/getFoulData', response={200: FoulDataResponse}, tags=['PASI'])
def get_foul_data(request, foul_number: int = 113148427, register_number: str = "HKR-999"):
    """
    Retrieve foul data from PASI by foul number and register number
    """
    req = PASIHandler.get_foul_data(foul_number, register_number)
    if req.status_code != 200:
        raise HttpError(req.status_code, req.json())
    return req.json()


@router.get('/getTransferData', response={200: TransferDataResponse, 404: Any}, tags=['PASI'])
def get_transfer_data(request, transfer_number: int = 11720143, register_number: str = "HKR-999"):
    """
    Retrieve transfer data from PASI by transfer number and register number
    """
    req = PASIHandler.get_transfer_data(transfer_number, register_number)
    if req.status_code != 200:
        raise HttpError(req.status_code, req.text)
    return req.json()


@router.post('/extendDueDate', response={200: ExtendDueDateResponse}, tags=['PASI'])
def extend_due_date(request, foul_data: FoulRequest):
    """
    Extend foul due date by 30 days
    """
    req = PASIHandler.extend_foul_due_date(foul_data)
    if req.status_code != 200:
        raise HttpError(req.status_code, req.json())
    return req.json()


@router.post('/saveObjection', tags=['PASI'])
def save_objection(request, objection: Objection):
    """
    Send a new objection to PASI
    """
    req = PASIHandler.save_objection(objection)
    return req.status_code


@router.get('/getDocuments', response={200: ATVDocumentResponse}, tags=['ATV'])
def get_atv_documents(request):
    """
    Retrieve all user documents from ATV with UUID
    """
    req = ATVHandler.get_documents()
    if req.status_code != 200:
        raise HttpError(req.status_code, req.json())
    return req.json()


@router.post('/sendDocument', tags=['ATV'])
def send_atv_document(request):
    """
    Upload new user document to ATV
    """
    req = ATVHandler.add_document()
    if req.status_code != 201:
        raise HttpError(req.status_code, req.json())
    return req.json()
