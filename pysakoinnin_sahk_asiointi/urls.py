"""pysakoinnin_sahk_asiointi URL Configuration"""

from django.http import HttpRequest
from django.urls import include, path
from helusers.oidc import RequestJWTAuthentication
from ninja import NinjaAPI
from ninja.errors import HttpError
from ninja.security import HttpBearer

from api.api import router as api_router
from api.parsers import StripParser
from gdpr_api.views import router as gdrp_api_router


class AuthBearer(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str):
        try:
            authenticator = RequestJWTAuthentication()
            user_auth = authenticator.authenticate(request=request)
            if user_auth is not None:
                request.user = user_auth.user
                return user_auth
        except Exception as error:
            raise HttpError(401, message=str(error))


api = NinjaAPI(
    title="Pysäköinnin asiointi",
    version="1.0.0",
    auth=AuthBearer(),
    parser=StripParser(),
)

api.add_router("/", api_router)
api.add_router("/gdpr", gdrp_api_router)


urlpatterns = [
    path("api/v1/", api.urls),
    path("helauth/", include("helusers.urls")),
    path("", include("helsinki_health_endpoints.urls")),
]
