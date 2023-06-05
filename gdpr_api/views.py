from django.http import HttpRequest, JsonResponse, HttpResponse
from environ import Env
from helusers.jwt import JWT
from helusers.oidc import OIDCConfig
from ninja import Router
from ninja.errors import HttpError
from ninja.security import HttpBearer

from api.views import ATVHandler

router = Router()

env = Env()


class JWTAuth(HttpBearer):
    def __init__(self, required_scope: str):
        self.required_scope = required_scope
        super().__init__()

    def authenticate(self, request: HttpRequest, token: str):
        oidc_config = OIDCConfig(env('GDPR_API_ISSUER'))

        jwt = JWT(token)
        try:
            issuer = jwt.issuer
        except KeyError:
            raise HttpError(401, message='Required "iss" claim is missing.')

        if issuer != env('GDPR_API_ISSUER'):
            raise HttpError(401, message="Unknown JWT issuer {}.".format(issuer))

        try:
            jwt.validate(oidc_config.keys(), env('GDPR_API_AUDIENCE'))
        except Exception:
            raise HttpError(401, message="JWT verification failed.")

        api_scopes = jwt.claims.get(env('TOKEN_AUTH_AUTHORIZATION_FIELD'), [])
        if self.required_scope not in api_scopes:
            print(self.required_scope)
            raise HttpError(401, message="No suitable API scope found")

        return jwt.claims.get("sub")


@router.get('/{user_id}', tags=["GDPR API"], auth=JWTAuth(required_scope=env("GDPR_API_QUERY_SCOPE")))
def get_user_info(request, user_id: str):
    if not request.auth or request.auth != user_id:
        raise HttpError(401, message="Unauthorised")
    req = ATVHandler.get_documents(user_id)

    if len(req['results']) <= 0:
        return HttpResponse(status=204)

    results = req['results']

    def get_key_val_pair(obj):
        _dict = {'key': 'CONTENT', 'children': []}

        def destructure_dict(val):
            _list = []
            for key in val:
                _list.append({
                    'key': key,
                    'value': val[key]
                })

            return _list

        for key in obj:
            if type(obj[key]) is dict:
                _dict['children'].append(
                    {'key': key,
                     'children': destructure_dict(obj[key])}
                )
            elif type(obj[key]) is list:
                for item in obj[key]:
                    _dict['children'].append(
                        {'key': key,
                         'children': destructure_dict(item)
                         }
                    )
            else:
                _dict['children'].append({
                    'key': key,
                    'value': obj[key]
                })

        return _dict

    return_obj = {
        'key': 'RESULTS',
        'children': []
    }

    for index in results:
        return_obj['children'].append(get_key_val_pair(index['content']))

    return return_obj


@router.delete('/{user_id}', tags=["GDPR API"], auth=JWTAuth(required_scope=env("GDPR_API_DELETE_SCOPE")))
def delete_user_info(request, user_id: str):
    if not request.auth or request.auth != user_id:
        raise HttpError(401, message="Unauthorised")

    req = ATVHandler.get_documents(user_id)

    if len(req['results']) <= 0:
        return HttpResponse(status=204)

    return JsonResponse(status=403, data={
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
                          "personuppgiftsansvarige (EU:s allmänna dataskyddsförordning Artikle 6 C)."
                }
            }
        ]
    })
