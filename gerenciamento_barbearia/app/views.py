from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import get_user_model
from django.db import transaction
from django.contrib.auth.models import Group
from .models import Visitor
from .groups import ADMIN_GROUP

from app.forms.change_password_form import ChangePasswordForm
from app.forms.create_visitor_form import CreateVisitorForm
from app.decorators import group_required
from .groups import USER_GROUP, ADMIN_GROUP

from uuid import uuid4


@login_required
def dashboard(request):
    return render(request, "dashboard.html")


@group_required(ADMIN_GROUP)
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





@group_required(ADMIN_GROUP)
def admin_painel(request):
    visitantes = Visitor.objects.select_related("user").order_by("-id")[:10]
    return render(request, "admin.html", {"total_visitantes": Visitor.objects.count(), "visitantes": visitantes,
})