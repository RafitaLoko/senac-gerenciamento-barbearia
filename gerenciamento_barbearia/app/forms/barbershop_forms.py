from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from app.models import Appointment, Service


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ["name", "description", "price", "duration_minutes", "active"]
        labels = {
            "name": "Nome",
            "description": "Descrição",
            "price": "Preço (R$)",
            "duration_minutes": "Duração (minutos)",
            "active": "Ativo",
        }

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise ValidationError("Informe o nome do serviço.")
        return name

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price <= 0:
            raise ValidationError("O preço deve ser maior que zero.")
        return price

    def clean_duration_minutes(self):
        duration = self.cleaned_data["duration_minutes"]
        if duration <= 0:
            raise ValidationError("A duração deve ser maior que zero.")
        return duration


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["service", "date", "time"]
        labels = {"service": "Serviço", "date": "Data", "time": "Horário"}
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "time": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["service"].queryset = Service.objects.filter(active=True)

    def clean_date(self):
        date = self.cleaned_data["date"]
        if date < timezone.localdate():
            raise ValidationError("Selecione uma data futura.")
        return date
