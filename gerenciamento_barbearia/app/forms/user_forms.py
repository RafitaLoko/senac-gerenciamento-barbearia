from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


class UserProfileForm(forms.ModelForm):
    email = forms.EmailField(label="E-mail")

    class Meta:
        model = get_user_model()
        fields = ["first_name", "email"]
        labels = {"first_name": "Nome"}

    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        users = get_user_model().objects.filter(email__iexact=email)
        if users.exclude(pk=self.instance.pk).exists():
            raise ValidationError("Este e-mail já está sendo usado por outra conta.")
        return email
