from ninja import Router
from ninja.errors import HttpError

from api.schemas import FoulDataResponse, ATVDocumentResponse
from api.views import *

router = Router()


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
