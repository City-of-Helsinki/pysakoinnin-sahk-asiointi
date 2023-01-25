from ninja import Router

from rectification.views import *

router = Router()


@router.get('/getDocuments')
def test_data(request):
    return ATVHandler.get_documents(request)


@router.post('/sendDocument')
def test_send(request):
    return ATVHandler.add_document(request)
