from django.contrib import admin
from django.urls import path

from views import ControlList

urlpatterns = [
    path('lista_kontroli/', ControlList.as_view(), name='lista-kontroli'),
]