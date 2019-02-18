from django.contrib import admin
from django.urls import path

from oceniarka.views import ControlList, ControlDocuments, EmailView, History
from oceniarka.widgets import ControlAutocomplete
urlpatterns = [
    path('lista_kontroli/', ControlList.as_view(), name='lista-kontroli'),
    path('podglad_kontroli/<int:control_id>/', ControlDocuments.as_view(),
         name='podglad-kontroli'),
    path('email/', EmailView.as_view(), name='email'),
    path('historia/', History.as_view(), name='historia'),
    path('control_autocomplete/', ControlAutocomplete.as_view(), name='control-autocomplete'),
]