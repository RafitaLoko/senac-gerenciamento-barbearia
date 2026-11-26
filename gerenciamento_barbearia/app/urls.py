from django.contrib.auth.views import LogoutView
from django.urls import path

from app.forms.authentication_form import CpfAuthenticationForm
from . import views

urlpatterns = [
    path("", views.dashboard, name="home"),
    path("dashboard/", views.dashboard, name="dashboard_cliente"),

    path("agendar/", views.agendar, name="agendar"),
<<<<<<< HEAD
    path("login/", views.RoleBasedLoginView.as_view(
=======
    path("login/", views.RoleBasedLoginView.as_view()),

    path("login/", views.CustomLoginView.as_view(

>>>>>>> 7c3646fbacc3880e6f32247259c1322020a38364
        template_name="login.html",
        authentication_form=CpfAuthenticationForm,
    ), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("admin-painel/", views.admin_painel, name="admin_painel"),
]