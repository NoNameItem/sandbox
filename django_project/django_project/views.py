from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from registration.backends.simple.views import RegistrationView
from django_project.models import UserProfile
from django_project.forms import ImageUploadForm, UserForm, UserProfileForm


class MyRegistrationView(RegistrationView):
    def get_success_url(self, request, user):
        return '/user/{0}'.format(user.username)

    def register(self, request, form):
        new_user = super().register(request, form)
        new_profile = UserProfile()
        new_profile.user = new_user
        new_profile.save()
        return new_user


def home(request):
    return render_to_response('django_project/home.html', RequestContext(request))


def profile(request, username):
    context = RequestContext(request)
    logged_user = request.user
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404

    user_profile = UserProfile.objects.filter(user=user)[0]
    return render_to_response("django_project/profile.html",
                              {"self": logged_user == user,
                               "get_user": user,
                               "user_profile": user_profile},
                              context)


@login_required
def change_photo(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise Http404
    logged_user = request.user
    if logged_user != user:
        raise PermissionDenied
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = user.userprofile
            user_profile.set_profile_image(request.FILES['image'])
    return HttpResponseRedirect('/user/{0}'.format(user.username))


def change_profile(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise Http404
    logged_user = request.user
    if logged_user != user:
        raise PermissionDenied
    user_profile = UserProfile.objects.filter(user=user)[0]

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        user_profile_form = UserProfileForm(request.POST)
        if user_form.is_valid() and user_profile_form.is_valid():
            user.first_name = user_form.cleaned_data['first_name']
            user.last_name = user_form.cleaned_data['last_name']
            user.email = user_form.cleaned_data['email']
            user.save()
            user_profile.sex = user_profile_form.cleaned_data['sex']
            user_profile.about = user_profile_form.cleaned_data['about']
            user_profile.save()
            return HttpResponseRedirect('/user/{0}'.format(user.username))
    else:
        user_form = UserForm()
        user_profile_form = UserProfileForm()
    return render_to_response('django_project/change_profile.html',
                              {'get_user': user,
                               'user_profile': user_profile,
                               'user_form': user_form,
                               'profile_form': user_profile_form},
                              RequestContext(request))


@login_required
def my_profile(request):
    return HttpResponseRedirect("/user/{0}".format(request.user.username))
