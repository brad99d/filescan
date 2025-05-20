from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('sign-up', views.signup, name='sign-up'),
    path('sign-in', LoginView.as_view(template_name='accounts/sign-in.html'), name='sign-in'),
    path('sign-out', LogoutView.as_view(template_name='accounts/sign-out.html'), name='sign-out'),
]