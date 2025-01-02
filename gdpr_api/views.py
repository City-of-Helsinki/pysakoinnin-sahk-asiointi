from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from ninja import Router
from ninja.errors import HttpError

from api.views import ATVHandler


def check_gdpr_permission(request: HttpRequest, user_id: str, scope: str) -> None:
    if request.user.uuid and str(request.user.uuid) != user_id:
        raise HttpError(403, message="Permission denied")

    if not request.auth.has_api_scopes(scope):
        raise HttpError(403, message=f"Token missing required scope {scope}")


router = Router()


@router.get("/{user_id}", tags=["GDPR API"])
def get_user_info(request, user_id: str):
    check_gdpr_permission(request, user_id, settings.GDPR_API_QUERY_SCOPE)

    req = ATVHandler.get_documents(user_id)

    if len(req["results"]) <= 0:
        return HttpResponse(status=204)

    results = req["results"]

    def get_key_val_pair(obj):
        _dict = {"key": "CONTENT", "children": []}

        def destructure_dict(val):
            _list = []
            for key in val:
                _list.append({"key": key, "value": val[key]})

            return _list

        for key in obj:
            if type(obj[key]) is dict:
                _dict["children"].append(
                    {"key": key, "children": destructure_dict(obj[key])}
                )
            elif type(obj[key]) is list:
                for item in obj[key]:
                    _dict["children"].append(
                        {"key": key, "children": destructure_dict(item)}
                    )
            else:
                _dict["children"].append({"key": key, "value": obj[key]})

        return _dict

    return_obj = {"key": "RESULTS", "children": []}

    for index in results:
        return_obj["children"].append(get_key_val_pair(index["content"]))

    return return_obj


@router.delete("/{user_id}", tags=["GDPR API"])
def delete_user_info(request, user_id: str):
    check_gdpr_permission(request, user_id, settings.GDPR_API_DELETE_SCOPE)

    req = ATVHandler.get_documents(user_id)

    if len(req["results"]) <= 0:
        return HttpResponse(status=204)

    return JsonResponse(
        status=403,
        data={
            "errors": [
                {
                    "code": "LEGAL_OBLIGATION",
                    "message": {
                        "en": "It is not possible to delete data. The processing is necessary for "
                        "compliance with a legal obligation of the controller "
                        "(EU General Data Protection Regulation Article 6 C).",
                        "fi": "Tietojen poisto ei ole mahdollista. Tietojen käsittely on tarpeen rekisterinpitäjän "
                        "lakisääteisen velvoitteen noudattamiseksi "
                        "(EU:n yleisen tietosuoja-asetus 6 artikla C-kohta).",
                        "sv": "Det är inte möjligt att radera uppgifter. Behandlingen är "
                        "nödvändig för att uppfylla en rättslig förpliktelse för den "
                        "personuppgiftsansvarige (EU:s allmänna dataskyddsförordning Artikle 6 C).",
                    },
                }
            ]
        },
    )
