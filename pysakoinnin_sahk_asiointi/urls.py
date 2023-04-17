"""pysakoinnin_sahk_asiointi URL Configuration """

from django.contrib import admin
from django.http import HttpRequest, HttpResponse
from django.urls import path
from helusers.oidc import RequestJWTAuthentication
from ninja import NinjaAPI
from ninja.errors import HttpError
from ninja.security import HttpBearer

from api.api import router as api_router


class AuthBearer(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str):
        try:
            authenticator = RequestJWTAuthentication()
            user_auth = authenticator.authenticate(request=request)
            if user_auth is not None:
                request.user = user_auth.user
                return True
        except Exception as error:
            raise HttpError(401, message=str(error))


api = NinjaAPI(title='Pysäköinnin asiointi', version='1.0.0', auth=AuthBearer())

api.add_router('/', api_router)


def health(request):
    return HttpResponse("OK", status=200, headers={'Content-Type': "application/json"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health),
    path("api/v1/", api.urls)
]
