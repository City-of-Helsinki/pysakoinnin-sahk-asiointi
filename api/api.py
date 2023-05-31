import copy

import ninja.errors
from django.http import HttpRequest, HttpResponse
from environ import Env
from ninja import Router, Schema
from ninja.security import HttpBearer

from api.schemas import FoulDataResponse, ATVDocumentResponse, TransferDataResponse, ExtendDueDateResponse, Objection, \
    DocumentStatusRequest
from api.utils import virus_scan_attachment_file
from api.views import PASIHandler, ATVHandler, DocumentHandler
from mail_service.audit_log import _commit_to_audit_log
from mail_service.utils import mail_constructor, extend_due_date_mail_constructor

router = Router()
env = Env()


class ApiKeyAuth(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str):
        if token == env("PASI_API_KEY"):
            return True


class FoulRequest(Schema):
    foul_number: int
    register_number: str


class NotFoundError(Schema):
    detail: str = "Resource not found"


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


@router.post('/extendDueDate', response={200: ExtendDueDateResponse, 400: None, 422: None}, tags=['PASI'])
def extend_due_date(request, foul_data: FoulRequest):
    """
    Extend foul due date by 30 days
    """
    req = PASIHandler.extend_foul_due_date(foul_data)

    try:
        ATVHandler.add_document(req, foul_data.foul_number, request.user.uuid, metadata={})
    except Exception as error:
        raise ninja.errors.HttpError(500, message=str(error))

    if req.status_code == 200:
        mail = extend_due_date_mail_constructor(new_due_date=req.json['dueDate'], lang='FI',
                                                mail_to='jaakko.ihanamaki@futurice.com')
        mail.send()
        
        if hasattr(mail, 'anymail_status'):
            _commit_to_audit_log(mail.to[0], mail.anymail_status)

    return req.json()


@router.post('/saveObjection', response={200: None, 204: None, 422: None}, tags=['PASI'])
def save_objection(request, objection: Objection):
    """
    Send a new objection to PASI
    """

    if hasattr(objection, "foulNumber") and objection.foulNumber is not None:
        objection_id = objection.foulNumber
    elif hasattr(objection, "transferNumber") and objection.transferNumber is not None:
        objection_id = objection.transferNumber
    else:
        raise ninja.errors.HttpError(422, message="Foul number or transfer number missing")

    if objection.attachments is not None and len(objection.attachments) > 0:
        try:
            for attachment in objection.attachments:
                virus_scan_attachment_file(attachment.data)
        except Exception:
            raise Exception

    if hasattr(objection, 'metadata') is None:
        objection.metadata = dict

    objection_without_attachments = copy.deepcopy(objection)
    del objection_without_attachments.attachments

    try:
        ATVHandler.add_document(objection_without_attachments, objection_id, user_id=request.user.uuid,
                                metadata={**objection.metadata})
    except Exception as error:
        raise ninja.errors.HttpError(500, message=str(error))

    req = PASIHandler.save_objection(objection, objection_id)
    return req.status_code


@router.get('/getDocuments/', response={200: ATVDocumentResponse}, tags=['ATV'])
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


@router.patch('/setDocumentStatus', response={200: None, 401: None, 404: NotFoundError, 422: None},
              tags=['Pysaköinnin asiointi'], auth=ApiKeyAuth())
def set_document_status(request, status_request: DocumentStatusRequest):
    """
    Update document status with ID and status
    """
    find_document_by_id = ATVHandler.get_document_by_transaction_id(status_request.id)
    document_id = find_document_by_id["results"][0]['id']

    req = DocumentHandler.set_document_status(document_id, status_request)

    if req.status_code == 200:
        mail = mail_constructor(event=status_request.status, lang=find_document_by_id['results'][0]['metadata']['lang'],
                                mail_to=find_document_by_id['results'][0]['content']['email'])
        mail.send()
        return HttpResponse(200)


@router.get('/testEmail', auth=None)
def testEmail(request):
    mail = mail_constructor(event='resolvedViaMail', lang='fI', mail_to='jaakko.ihanamaki@futurice.com')
    mail.send()
    if hasattr(mail, 'anymail_status'):
        _commit_to_audit_log(mail.to[0], mail.anymail_status)
