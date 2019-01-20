from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import logout_then_login
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View

from autentykacja.forms import LoginForm, ChangePasswordForm

from autentykacja.apps import AutentykacjaConfig
from intra.settings import LOGIN_URL, LOGIN_REDIRECT_URL

APP_NAME = AutentykacjaConfig.name
START_PAGE = reverse_lazy(LOGIN_REDIRECT_URL)
TEMPLATE = f'{APP_NAME}/autentykacja.html'


class LoginUserView(View):

    def get(self, request):
        form = LoginForm()
        return render(request, TEMPLATE, locals())

    def post(self, request):
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            next_url = request.GET.get('next')
            user = authenticate(username=username, password=password)

            if user:
                last_login = User.objects.get(username=username).last_login
                login(request, user)

                if last_login is None:
                    return redirect(reverse_lazy('change-password'))

                if next_url:
                    return redirect(next_url)

                return redirect(START_PAGE)

        # messages.error(request, 'Zły login lub hasło')
        form.add_error(None, 'Zły login lub hasło')
        return render(request, TEMPLATE, locals())


class ChangePasswordView(LoginRequiredMixin, View):
    login_url = LOGIN_URL  # wymagane przez LoginRequiredMixin

    def get(self, request):
        form = ChangePasswordForm
        return render(request, TEMPLATE, locals())

    def post(self, request):
        form = ChangePasswordForm(request.POST)

        if form.is_valid():
            password1 = form.cleaned_data.get('password1')
            password2 = form.cleaned_data.get('password2')

            if password1 == password2:
                user = get_object_or_404(User, id=request.user.pk)
                user.set_password(password1)
                user.save()

                user = authenticate(username=user.username, password=password1)

                if user:
                    login(request, user)

                    messages.success(request, 'Hasło zostało zmienione')
                    return redirect(START_PAGE)

            else:
                form.add_error(None, 'Hasła nie są takie same')
                return render(request, TEMPLATE, locals())

        return redirect(START_PAGE)


class LogoutUserView(View):

    def get(self, request):
        return logout_then_login(request, login_url=LOGIN_URL)



