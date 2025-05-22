from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import UsernameUpdateForm
from django.db.models import Count, Prefetch
from scan.models import AnalysisResult
from scan import scanner
from scan.views import shorten_filename, format_file_size, process_results

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
@login_required()
def admin_view(request):
    # get all results for every user
    users = User.objects.annotate(
        result_count=Count('analysis_results')
    ).prefetch_related(
        Prefetch('analysis_results', queryset=AnalysisResult.objects.order_by('-created_at'))
    )
    # process the data
    processed_users = []
    for user in users:
        processed_results = process_results(user.analysis_results.all())
        processed_users.append({
            'id': user.id,
            'username': user.username,
            'is_staff': user.is_staff,
            'result_count': user.result_count,
            'results': processed_results,
        })
    return render(request, 'settings/manage.html', {
        'users': processed_users
    })

@user_passes_test(lambda u: u.is_staff)
@login_required()
def promote(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_staff = True
    user.save()
    return redirect('manage')

@user_passes_test(lambda u: u.is_staff)
@login_required()
def demote(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_staff = False
    user.save()
    return redirect('manage')