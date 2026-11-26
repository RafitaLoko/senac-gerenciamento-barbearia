from django.contrib.auth.views import LogoutView
from django.urls import path
from django.views.generic import RedirectView

from app.forms.authentication_form import CpfAuthenticationForm
from . import views

urlpatterns = [
<<<<<<< HEAD
    path("", views.RoleBasedLoginView.as_view(
        template_name="login.html",
        authentication_form=CpfAuthenticationForm,
    ), name="home"),
    path("cadastro/", views.register, name="cadastro"),
=======
    path("", RedirectView.as_view(pattern_name="login"), name="root"),
    path("dashboard/", views.dashboard, name="home"),
>>>>>>> 833d416067b6958abc6a2f8ef51015653ab540ce
    path("dashboard/", views.dashboard, name="dashboard_cliente"),

    path("agendar/", views.agendar, name="agendar"),

<<<<<<< HEAD
    path("login/", views.RoleBasedLoginView.as_view(
=======


    path("login/", views.CustomLoginView.as_view(


>>>>>>> 833d416067b6958abc6a2f8ef51015653ab540ce
        template_name="login.html",
        authentication_form=CpfAuthenticationForm,
    ), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("admin-painel/", views.admin_painel, name="admin_painel"),

]