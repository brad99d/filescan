from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import UsernameUpdateForm

# Create your views here.
@login_required()
def profile(request):
    user = request.user
    username_form = UsernameUpdateForm(instance=user)
    password_form = PasswordChangeForm(user=user)
    if request.method == 'POST':
        if 'update_username' in request.POST:
            success = False
            username_form = UsernameUpdateForm(request.POST, instance=user)
            if username_form.is_valid():
                username_form.save()
                success = True
            return render(request, 'settings/profile.html', {
                'username_success': success,
                'username_form': username_form,
                'password_form': PasswordChangeForm(user=user),
            })
        elif 'update_password' in request.POST:
            success = False
            password_form = PasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                success = True
            return render(request, 'settings/profile.html', {
                'password_success': success,
                'username_form': UsernameUpdateForm(instance=user),
                'password_form': PasswordChangeForm(user=user),
            })
    return render(request, 'settings/profile.html', {
        'username_form': username_form,
        'password_form': password_form,
    })

@user_passes_test(lambda u: u.is_staff)
def admin_view(request):
    users = User.objects.all()
    return render(request, 'settings/manage.html', {'users': users})