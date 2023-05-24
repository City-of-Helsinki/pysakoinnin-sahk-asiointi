from django.http import HttpRequest
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
    return req


@router.delete('/{user_id}', tags=["GDPR API"], auth=JWTAuth(required_scope=env("GDPR_API_DELETE_SCOPE")))
def delete_user_info(request, user_id: str):
    if not request.auth or request.auth != user_id:
        raise HttpError(401, message="Unauthorised")

    raise HttpError(403, message="Tietojen poisto ei ole mahdollista lain xyz velvoittamana")
