from ninja import Router

from api.views import ATVHandler

router = Router()


@router.get('/{user_id}/', tags=["GDPR API"], auth=None)
def get_user_info(request, user_id):
    documents = ATVHandler.get_documents(user_id)["results"]
    for document in documents:
        del document["content"]["attachments"]

    return documents


@router.delete('/{user_id}/', tags=["GDPR API"])
def delete_user_info(request):
    return 403
