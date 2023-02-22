from ninja import Router
from ninja.errors import HttpError

from api.views import *

router = Router()


@router.get("/helloworld")
def helloworld(request):
    return {"msg": 'Hello world'}


@router.get('/getFoulData')
def test_pasi(request, foul_number: int = 113148427, register_number: str = "HKR-999"):
    req = PASIHandler.getFoulData(request, foul_number, register_number)
    if req.status_code != 200:
        raise HttpError(req.status_code, req.json())
    return req.json()


@router.get('/getDocuments')
def test_data(request):
    req = ATVHandler.get_documents(request)
    if req.status_code != 200:
        raise HttpError(req.status_code, req.json())
    return req.json()


@router.post('/sendDocument')
def test_send(request):
    req = ATVHandler.add_document(request)
    if req.status_code != 201:
        raise HttpError(req.status_code, req.json())
    return req.json()
