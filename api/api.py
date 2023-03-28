from django.http import HttpRequest
from environ import Env
from helusers.oidc import RequestJWTAuthentication
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.security import HttpBearer

from api.schemas import FoulDataResponse, ATVDocumentResponse, ExtendDueDateResponse, TransferDataResponse, Objection, \
    DocumentStatusRequest
from api.views import PASIHandler, ATVHandler, DocumentHandler

router = Router()
env = Env()


class AuthBearer(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str):
        try:
            authenticator = RequestJWTAuthentication()
            user_auth = authenticator.authenticate(request=request)
            if user_auth is not None:
                request.user = user_auth.user
                return True
        except Exception as error:
            raise HttpError(401, message=str(error))


class ApiKeyAuth(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str):
        if token == env("PASI_API_KEY"):
            return True


class FoulRequest(Schema):
    foul_number: int
    register_number: str


class NotFoundError(Schema):
    detail: str = "Resource not found"


@router.get("/helloworld")
def helloworld(request):
    return {"msg": 'Hello world'}


@router.get('/tryAuth', auth=AuthBearer())
def try_auth(request):
    return "ping!"


@router.get('/getFoulData', response={200: FoulDataResponse, 404: NotFoundError}, tags=['PASI'])
def get_foul_data(request, foul_number: int = 113148427, register_number: str = "HKR-999"):
    """
    Retrieve foul data from PASI by foul number and register number
    """
    req = PASIHandler.get_foul_data(foul_number, register_number)
    return req.json()


@router.get('/getTransferData', response={200: TransferDataResponse, 404: NotFoundError}, tags=['PASI'])
def get_transfer_data(request, transfer_number: int = 11720143, register_number: str = "HKR-999"):
    """
    Retrieve transfer data from PASI by transfer number and register number
    """
    req = PASIHandler.get_transfer_data(transfer_number, register_number)
    return req.json()


@router.post('/extendDueDate', response={200: ExtendDueDateResponse, 422: None}, tags=['PASI'])
def extend_due_date(request, foul_data: FoulRequest):
    """
    Extend foul due date by 30 days
    """
    req = PASIHandler.extend_foul_due_date(foul_data)
    return req.json()


@router.post('/saveObjection', response={200: None, 204: None, 422: None}, tags=['PASI'])
def save_objection(request, objection: Objection):
    """
    Send a new objection to PASI
    """
    req = PASIHandler.save_objection(objection)
    return req.json()


@router.get('/getDocuments/', response={200: ATVDocumentResponse}, tags=['ATV'], auth=AuthBearer())
def get_atv_documents(request):
    """
    Retrieve all user documents from ATV with UUID
    """
    req = ATVHandler.get_documents(request.user.uuid)
    return req


@router.get('/getDocumentByTransactionId/{id}', response={200: ATVDocumentResponse, 404: NotFoundError, 500: None},
            tags=["ATV"])
def get_document_by_transaction_id(request, id):
    """
    Get document from ATV by foul ID
    """
    req = ATVHandler.get_document_by_transaction_id(id)
    return req


@router.post('/sendObjection/{foul_id}',
             response={200: None, 201: ATVDocumentResponse, 400: None, 401: None},
             tags=['ATV'],
             auth=AuthBearer())
def send_objection_to_atv(request, objection: Objection, foul_id: str):
    """
    Upload new user document to ATV
    """
    req = ATVHandler.add_document(objection, foul_id, user_id=request.user.uuid)
    return req


@router.patch('/setDocumentStatus', response={200: None, 401: None, 404: NotFoundError, 422: None},
              tags=['Pysaköinnin asiointi'], auth=ApiKeyAuth())
def set_document_status(request, status_request: DocumentStatusRequest):
    """
    Update document status with ID and status
    """
    return DocumentHandler.set_document_status(status_request)
