from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.contrib.auth.models import Group

from django.urls import reverse
from .models import Visitor


from app.forms.change_password_form import ChangePasswordForm
from app.forms.create_visitor_form import CreateVisitorForm
from app.decorators import group_required
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
        return reverse("dashboard_cliente")


@login_required
def dashboard(request):
    if request.user.is_superuser or request.user.groups.filter(name__in=ADMIN_GROUPS).exists():
        return redirect("admin_painel")
    return render(request, "dashboard.html")


@login_required
def agendar(request):
    return render(request, "agendar.html")


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
                user.groups.add(Group.objects.get(name=USER_GROUP))
                
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
    return render(request, "admin.html", {"total_visitantes": Visitor.objects.count(), "visitantes": visitantes,
})

class CustomLoginView(LoginView):
    def get_success_url(self):
        if self.request.user.groups.filter(name__in=ADMIN_GROUPS).exists():
            return reverse("admin_painel")
        return super().get_success_url()

@login_required
def agendar(request):
    return render(request, "dashboard.html")