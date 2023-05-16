from django.http import HttpRequest
from environ import Env
from helusers._oidc_auth_impl import resolve_user
from helusers.oidc import ApiTokenAuthentication
from ninja import Router
from ninja.errors import HttpError
from ninja.security import HttpBearer

from api.views import ATVHandler

router = Router()

env = Env()


class OIDC_API_TOKEN_AUTH():
    def __init__(self):
        self.AUTH_SCHEME = 'Bearer'
        self.AUDIENCE = env('GDPR_API_AUDIENCE')
        self.ISSUER = env('GDPR_API_ISSUER')
        self.API_AUTHORIZATION_FIELD = env('GDPR_API_AUTH_FIELD')
        self.API_SCOPE_PREFIX = env('TOKEN_AUTH_SCOPE_PREFIX')
        self.USER_RESOLVER = resolve_user
        self.REQUIRE_API_SCOPE_FOR_AUTHENTICATION = True
        self.OIDC_CONFIG_EXPIRATION_TIME = 600


class JWTAuth(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str):
        auth = ApiTokenAuthentication(settings=OIDC_API_TOKEN_AUTH())
        result = auth.authenticate(request)
        if result is not None:
            return True
        else:
            raise HttpError(401, message="Unauthorised")


@router.get('/{user_id}', tags=["GDPR API"], auth=JWTAuth())
def get_user_info(request, user_id):
    req = ATVHandler.get_documents(user_id)
    return req


@router.delete('/{user_id}/', tags=["GDPR API"], auth=JWTAuth())
def delete_user_info(request):
    raise HttpError(403, message="Tietojen poisto ei ole mahdollista lain xyz velvoittamana")
