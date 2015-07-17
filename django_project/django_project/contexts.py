__author__ = 'nonameitem'
from settings import PROJECTS


def project_list(request):
    return {'projects': PROJECTS}