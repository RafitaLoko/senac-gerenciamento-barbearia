from django.contrib.auth.views import LogoutView
from django.urls import path

from app.forms.authentication_form import CpfAuthenticationForm
from . import views

urlpatterns = [
    path("", views.RoleBasedLoginView.as_view(
        template_name="login.html",
        authentication_form=CpfAuthenticationForm,
    ), name="home"),
    path("cadastro/", views.register, name="cadastro"),
    path("dashboard/", views.dashboard, name="dashboard_cliente"),
    path("agendar/", views.agendar, name="agendar"),
    path("servicos/", views.servicos, name="servicos"),
    path("meus-agendamentos/", views.meus_agendamentos, name="meus_agendamentos"),
    path("meus-agendamentos/<int:appointment_id>/cancelar/", views.cancelar_agendamento, name="cancelar_agendamento"),
    path("perfil/", views.perfil, name="perfil"),
    path("confirmacao/<int:appointment_id>/", views.confirmacao, name="confirmacao"),
    path("login/", views.CustomLoginView.as_view(
        template_name="login.html",
        authentication_form=CpfAuthenticationForm,
    ), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("admin-painel/", views.admin_painel, name="admin_painel"),
    path("admin/agendamentos/", views.admin_agendamentos, name="admin_agendamentos"),
    path("admin/clientes/", views.admin_clientes, name="admin_clientes"),
    path("admin/servicos/", views.admin_servicos, name="admin_servicos"),
    path("admin/servicos/<int:service_id>/editar/", views.admin_editar_servico, name="admin_editar_servico"),
    path("admin/servicos/<int:service_id>/excluir/", views.admin_excluir_servico, name="admin_excluir_servico"),
    path("admin/relatorios/", views.admin_relatorios, name="admin_relatorios"),
]