from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.contrib.auth.models import Group



from django.contrib.auth.views import LoginView



from django.urls import reverse
from django.db.models import Count, Sum
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Appointment, Service, Visitor
from app.forms.barbershop_forms import AppointmentForm, ServiceForm
from app.forms.change_password_form import ChangePasswordForm
from app.forms.create_visitor_form import CreateVisitorForm
from app.decorators import group_required

<<<<<<< HEAD
=======

>>>>>>> e402640b78abbcf26ec5ed86a34d679b9809c0b4
from .groups import USER_GROUP, ADMIN_GROUPS


from uuid import uuid4


class RoleBasedLoginView(LoginView):
    template_name = "login.html"

    def get_success_url(self):
        redirect_url = self.get_redirect_url()
        if redirect_url:
            return redirect_url

        user = self.request.user
        if user.is_superuser or user.groups.filter(name__in=ADMIN_GROUPS).exists():
            return reverse("admin_painel")
        return reverse("agendar")


@login_required
def dashboard(request):
    if request.user.is_superuser or request.user.groups.filter(name__in=ADMIN_GROUPS).exists():
        return redirect("admin_painel")
    appointments = Appointment.objects.filter(client=request.user)
    upcoming = appointments.exclude(status=Appointment.STATUS_CANCELLED).filter(
        date__gte=timezone.localdate()
    ).order_by("date", "time").first()
    return render(request, "dashboard.html", {
        "total": appointments.count(),
        "upcoming": upcoming,
    })


@login_required
def agendar(request):
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.client = request.user
            if appointment.date < timezone.localdate():
                form.add_error("date", "Selecione uma data futura.")
            else:
                appointment.save()
                messages.success(request, "Agendamento confirmado!")
                return redirect("confirmacao", appointment_id=appointment.pk)
    else:
        form = AppointmentForm()
    return render(request, "agendar.html", {"form": form})


@login_required
def servicos(request):
    return render(request, "servico.html", {"services": Service.objects.filter(active=True)})


@login_required
def meus_agendamentos(request):
    appointments = Appointment.objects.filter(client=request.user)
    return render(request, "agendamento.html", {"appointments": appointments})


@login_required
def cancelar_agendamento(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id, client=request.user)
    if request.method == "POST" and appointment.status not in (
        Appointment.STATUS_CANCELLED,
        Appointment.STATUS_COMPLETED,
    ):
        appointment.status = Appointment.STATUS_CANCELLED
        appointment.save(update_fields=["status"])
        messages.success(request, "Agendamento cancelado.")
    return redirect("meus_agendamentos")


@login_required
def perfil(request):
    if request.method == "POST":
        request.user.first_name = request.POST.get("first_name", "").strip()
        request.user.email = request.POST.get("email", "").strip()
        request.user.save(update_fields=["first_name", "email"])
        messages.success(request, "Perfil atualizado.")
        return redirect("perfil")
    return render(request, "perfil.html")


@login_required
def confirmacao(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id, client=request.user)
    return render(request, "confirmacao.html", {"appointment": appointment})


def register(request):
    if request.method == "POST":
        form = CreateVisitorForm(request.POST)

        if form.is_valid():
            User = get_user_model()

            with transaction.atomic():
                user = User.objects.create_user(
                    username=form.cleaned_data["cpf"],
                    password=form.cleaned_data["password"],
                )
                visitor = form.save(commit=False)
                visitor.user = user
                visitor.save()
                group, _ = Group.objects.get_or_create(name=USER_GROUP)
                user.groups.add(group)

            messages.success(request, "Cadastro realizado. Entre com sua conta.")
            return redirect("login")
    else:
        form = CreateVisitorForm()

    return render(request, "cadastro.html", {"form": form})


@group_required(*ADMIN_GROUPS)
def create_visitor(request):
    if request.method == 'POST':
        visitor_form = CreateVisitorForm(request.POST)
        
        if visitor_form.is_valid():
            User = get_user_model()

            with transaction.atomic():
                visitor = visitor_form.save(commit=False)
                visitor.ticket_number = str(uuid4())
                visitor.save()

                user = User.objects.create_user(
                    username=visitor.cpf,
                    password=visitor_form.cleaned_data['password'],
                )
                visitor.user = user
                visitor.save(update_fields=['user'])
                group, _ = Group.objects.get_or_create(name=USER_GROUP)
                user.groups.add(group)

                
            return redirect('visitors')
    else:
        visitor_form = CreateVisitorForm()
        
    response = { 
        'form': visitor_form 
    }
        
    return render(request, 'create-visitor.html', response)

@group_required(USER_GROUP)
def change_password(request):
    if request.method == "POST":
        form = ChangePasswordForm(request.POST, user=request.user)

        if form.is_valid():
            request.user.set_password(form.cleaned_data["new_password"])
            request.user.save()
            update_session_auth_hash(request, request.user)
            return redirect("my_visitor")
    else:
        form = ChangePasswordForm(user=request.user)

    return render(request, "change-password.html", {"form": form})





@group_required(*ADMIN_GROUPS)
def admin_painel(request):
    visitantes = Visitor.objects.select_related("user").order_by("-id")[:10]
<<<<<<< HEAD
    return render(request, "admin.html", {
        "total_visitantes": Visitor.objects.count(),
        "visitantes": visitantes,
        "total_agendamentos": Appointment.objects.count(),
        "total_servicos": Service.objects.count(),
        "agendamentos_pendentes": Appointment.objects.filter(status=Appointment.STATUS_PENDING).count(),
    })


=======
    return render(request, "admin.html", {"total_visitantes": Visitor.objects.count(), "visitantes": visitantes,
})
>>>>>>> e402640b78abbcf26ec5ed86a34d679b9809c0b4

class CustomLoginView(LoginView):
    def get_success_url(self):
        redirect_url = self.get_redirect_url()
        if redirect_url:
            return redirect_url
        if self.request.user.is_superuser or self.request.user.groups.filter(name__in=ADMIN_GROUPS).exists():
            return reverse("admin_painel")
        return reverse("agendar")


<<<<<<< HEAD
@group_required(*ADMIN_GROUPS)
def admin_agendamentos(request):
    if request.method == "POST":
        appointment = get_object_or_404(Appointment, pk=request.POST.get("appointment_id"))
        status = request.POST.get("status")
        if status in dict(Appointment.STATUS_CHOICES):
            appointment.status = status
            appointment.save(update_fields=["status"])
            messages.success(request, "Status do agendamento atualizado.")
    appointments = Appointment.objects.select_related("client", "service").all()
    return render(request, "admin_agendamentos.html", {
        "appointments": appointments,
        "status_choices": Appointment.STATUS_CHOICES,
    })


@group_required(*ADMIN_GROUPS)
def admin_clientes(request):
    clients = get_user_model().objects.filter(groups__name=USER_GROUP).annotate(
        total_appointments=Count("appointments")
    ).distinct()
    return render(request, "cliente.html", {"clients": clients})


@group_required(*ADMIN_GROUPS)
def admin_servicos(request):
    if request.method == "POST":
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Serviço cadastrado.")
            return redirect("admin_servicos")
    else:
        form = ServiceForm()
    return render(request, "admin_servicos.html", {
        "form": form,
        "services": Service.objects.all(),
    })


@group_required(*ADMIN_GROUPS)
def admin_editar_servico(request, service_id):
    service = get_object_or_404(Service, pk=service_id)
    if request.method == "POST":
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, "Serviço atualizado.")
            return redirect("admin_servicos")
    else:
        form = ServiceForm(instance=service)
    return render(request, "admin_servicos.html", {
        "form": form,
        "services": Service.objects.all(),
        "editing": service,
    })


@group_required(*ADMIN_GROUPS)
def admin_excluir_servico(request, service_id):
    service = get_object_or_404(Service, pk=service_id)
    if request.method == "POST":
        if service.appointments.exists():
            messages.error(request, "Não é possível excluir um serviço com agendamentos.")
        else:
            service.delete()
            messages.success(request, "Serviço excluído.")
    return redirect("admin_servicos")


@group_required(*ADMIN_GROUPS)
def admin_relatorios(request):
    by_status = Appointment.objects.values("status").annotate(total=Count("id")).order_by("status")
    revenue = Appointment.objects.filter(status=Appointment.STATUS_COMPLETED).aggregate(
        total=Sum("service__price")
    )["total"] or 0
    return render(request, "relatorios.html", {
        "revenue": revenue,
        "by_status": by_status,
        "total_agendamentos": Appointment.objects.count(),
    })
=======
>>>>>>> e402640b78abbcf26ec5ed86a34d679b9809c0b4

