from ninja import Router
from ninja.errors import HttpError
from requests import request as HTTPRequest

from rectification.views import *

router = Router()


@router.get('/getDocuments')
def test_data(request):
    req = ATVHandler.get_documents(request)
    if req.status_code != 200:
        raise HttpError(req.status_code, req.json())
    return req.json()


@router.get('/testPasi')
def test_pasi(request):
    req = HTTPRequest("GET", url="https://10.182.254.208:8443")
    return req.json()


@router.post('/sendDocument')
def test_send(request):
    req = ATVHandler.add_document(request)
    if req.status_code != 201:
        raise HttpError(req.status_code, req.json())
    return req.json()
