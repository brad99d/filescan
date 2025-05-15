from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

# Create your views here.
def dashboard(request):
    template = loader.get_template('scan/dashboard.html')
    return HttpResponse(template.render({}, request))

def profile(request):
    template = loader.get_template('scan/profile.html')
    return HttpResponse(template.render({}, request))