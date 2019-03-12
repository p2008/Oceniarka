from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label='Identyfikator', max_length=6, required=True)
    password = forms.CharField(label='Hasło', max_length=64,
                               widget=forms.PasswordInput, required=True)


class ChangePasswordForm(forms.Form):
    password1 = forms.CharField(label='Podaj hasło', widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label='Powtórz hasło', widget=forms.PasswordInput, required=True)



