from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from registration.backends.simple.views import RegistrationView


class MyRegistrationView(RegistrationView):
    def get_success_url(self, request, user):
        return '/'


def home(request):
    return render_to_response('django_project/home.html', {}, RequestContext(request))
