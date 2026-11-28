from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm


class CpfAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="CPF ou e-mail")
    password = forms.CharField(strip=False)

    def clean(self):
        identifier = self.cleaned_data.get("username", "").strip()
        if "@" in identifier:
            matching_users = list(
                get_user_model()._default_manager.filter(email__iexact=identifier)[:2]
            )
            if len(matching_users) == 1:
                self.cleaned_data["username"] = matching_users[0].get_username()
        else:
            self.cleaned_data["username"] = identifier
        return super().clean()