from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

# Create your views here.
def home(request):
    template = loader.get_template('accounts/home.html')
    return HttpResponse(template.render({}, request))

def signup(request):
    template = loader.get_template('accounts/sign-up.html')
    return HttpResponse(template.render({}, request))

def signin(request):
    template = loader.get_template('accounts/sign-in.html')
    return HttpResponse(template.render({}, request))