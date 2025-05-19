from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User

# Create your views here.
@login_required()
def profile(request):
    return render(request, 'settings/profile.html')

@user_passes_test(lambda u: u.is_staff)
def admin_view(request):
    users = User.objects.all()
    return render(request, 'settings/manage.html', {'users': users})