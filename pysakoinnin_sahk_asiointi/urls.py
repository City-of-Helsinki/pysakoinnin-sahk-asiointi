"""pysakoinnin_sahk_asiointi URL Configuration """

from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

from api.api import router as api_router

api = NinjaAPI(title='Pysäköinnin asiointi', version='1.0.0')

api.add_router('/', api_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", api.urls)
]
