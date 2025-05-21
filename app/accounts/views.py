from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your views here.
def home(request):
    template = loader.get_template('accounts/home.html')
    return HttpResponse(template.render({}, request))

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/sign-up.html', {'form': form})

# give admin to the first user
@receiver(post_save, sender=User)
def grant_admin_to_first_user(sender, instance, created, **kwargs):
    if created and User.objects.count() == 1:
        instance.is_superuser = True
        instance.is_staff = True
        instance.save()