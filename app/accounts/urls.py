from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('sign-up', views.signup, name='sign-up'),
    path('sign-in', views.signin, name='sign-in'),
]