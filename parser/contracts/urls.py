from django.urls import path
from . import views


urlpatterns = [
    path("contracts/upload", views.contract_upload, name="contract_upload"),
    path("contracts/<int:contract_id>/status", views.contract_status, name="contract_status"),
    path("contracts/<int:contract_id>", views.contract_detail, name="contract_detail"),
    path("contracts", views.contract_list, name="contract_list"),
    path("contracts/<int:contract_id>/download", views.contract_download, name="contract_download"),
]



