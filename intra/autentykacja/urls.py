from django.urls import path
from autentykacja.views import LoginUserView, LogoutUserView, \
    ChangePasswordView

urlpatterns = [
    path('login/', LoginUserView.as_view(), name='login'),
    path('logout/', LogoutUserView.as_view(), name='logout'),
    path('change_password/', ChangePasswordView.as_view(),
         name='change-password'),
]
