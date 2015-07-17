__author__ = 'nonameitem'
from django_project.settings import PROJECTS


def project_list(request):
    return {'projects': PROJECTS}