from django.contrib import admin
from django.urls import path

from oceniarka.views import ControlList, ControlDocuments

urlpatterns = [
    path('lista_kontroli/', ControlList.as_view(), name='lista-kontroli'),
    path('podglad_kontroli/<int:control_id>/', ControlDocuments.as_view(),
         name='podglad-kontroli'),
]