__author__ = 'nonameitem'
from django_project.settings import PROJECTS


def project_list(request):
    return {'projects': sorted(PROJECTS, key=lambda x: x[1])}
