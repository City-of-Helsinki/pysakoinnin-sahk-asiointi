"""pysakoinnin_sahk_asiointi URL Configuration """

from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

api = NinjaAPI()


@api.get("/helloworld")
def helloworld(request):
    return {"msg": 'Hello world'}


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls)
]
