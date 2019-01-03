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
                login(request, user)

                if next_url:
                    return redirect(next_url)

                return redirect(START_PAGE)

        form.add_error(None, 'Zły login lub hasło')
        return render(request, TEMPLATE, locals())


class Password(View):

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
                messages.success(request, 'Hasło zostało zmienione')
            else:
                form.add_error('password1', 'Hasła nie są takie same')
                return redirect(reverse_lazy('change'))

        return redirect(START_PAGE)


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
                messages.success(request, 'Hasło zostało zmienione')
            else:
                form.add_error('password1', 'Hasła nie są takie same')
                return redirect(reverse_lazy('change'))

        return redirect(START_PAGE)


class LogoutUserView(View):

    def get(self, request):
        return logout_then_login(request, login_url=LOGIN_URL)



