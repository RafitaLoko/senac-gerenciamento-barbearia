import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from ..models import Visitor


class CreateVisitorForm(forms.ModelForm):
    email = forms.EmailField(label="E-mail")
    password = forms.CharField(strip=False)
    confirm_password = forms.CharField(strip=False)

    class Meta:
        model = Visitor
        fields = ["cpf"]

    def clean_cpf(self):
        cpf = self.cleaned_data["cpf"].strip()
        if not re.fullmatch(r"[0-9]{11}", cpf):
            raise ValidationError("Informe um CPF com 11 números.")

        User = get_user_model()
        if User.objects.filter(username=cpf).exists():
            raise ValidationError("Já existe uma conta cadastrada com esse CPF.")
        return cpf

    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise ValidationError("Já existe uma conta cadastrada com esse e-mail.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:
            if password != confirm_password:
                self.add_error("confirm_password", "As senhas não coincidem.")
            else:
                User = get_user_model()
                candidate_user = User(
                    username=cleaned_data.get("cpf"),
                    email=cleaned_data.get("email"),
                )

                try:
                    validate_password(password, candidate_user)
                except ValidationError as error:
                    self.add_error("password", error)

        return cleaned_data