"""pysakoinnin_sahk_asiointi URL Configuration"""

from django.http import HttpRequest, HttpResponse
from django.urls import include, path
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_safe
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


#
# Kubernetes liveness & readiness probes
#
@require_safe
@never_cache
def health(*_, **__):
    return HttpResponse("OK", status=200)


@require_safe
@never_cache
def readiness(*_, **__):
    failed_check = False
    try:
        from django.db import connections

        for name in connections:
            cursor = connections[name].cursor()
            cursor.execute("SELECT 1;")
            row = cursor.fetchone()
            if row is None:
                failed_check = True
    except Exception:
        failed_check = True

    if failed_check:
        raise HttpError(500, message="Database issue")

    return HttpResponse("OK", status=200)


urlpatterns = [
    path("health/", health),
    path("readiness/", readiness),
    path("api/v1/", api.urls),
    path("helauth/", include("helusers.urls")),
]
