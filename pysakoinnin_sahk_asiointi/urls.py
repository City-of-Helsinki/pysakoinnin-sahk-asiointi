"""pysakoinnin_sahk_asiointi URL Configuration """

from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

from api.api import router as api_router

api = NinjaAPI()

api.add_router('/api/v1', api_router)


@api.get("/helloworld")
def helloworld(request):
    return {"msg": 'Hello world'}


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", api.urls)
]
