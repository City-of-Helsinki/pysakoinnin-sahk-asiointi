"""pysakoinnin_sahk_asiointi URL Configuration """

from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

from rectification.api import router as rectification_router

api = NinjaAPI()

api.add_router('/rectification/', rectification_router)


@api.get("/helloworld")
def helloworld(request):
    return {"msg": 'Hello world'}


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls)
]
