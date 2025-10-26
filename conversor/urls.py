from django.urls import path, include
from . import views
from django.urls import path

urlpatterns = [
    # status / teste rápido
    path("", views.conversor_status, name="conversor_status"),

    # Excel -> JSON
    # Envie multipart/form-data com campo 'arquivo_excel'
    path("upload-excel/", views.excel_para_json_view, name="excel_para_json"),

    # JSON -> Excel
    # Envie uma lista JSON no corpo do POST
    path("gerar-excel/", views.json_para_excel_view, name="json_para_excel"),
]
