from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

# Create your views here.
def profile(request):
    template = loader.get_template('settings/profile.html')
    return HttpResponse(template.render({}, request))