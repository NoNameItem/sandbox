from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from registration.backends.simple.views import RegistrationView

from django_project.models import UserProfile
from django_project.forms import ImageUploadForm, UserForm, UserProfileForm
from chat.models import Chat
from chat.forms import PrivateChatForm
from utils import get_private_chats


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
    private_chats = None
    private_chat_form = None
    open_new_chat_form = False
    context = RequestContext(request)

    logged_user = request.user
    user = get_object_or_404(User, username=username)
    user_profile = UserProfile.objects.filter(user=user)[0]

    if request.user != user:
        private_chats = get_private_chats(request.user, user)
        if request.method != 'POST':
            new_private_chat = Chat()
            new_private_chat.name = "{0} <-> {1}".format(request.user.username, user.username)
            private_chat_form = PrivateChatForm(instance=new_private_chat)
        else:
            private_chat_form = PrivateChatForm(request.POST)
            if private_chat_form.is_valid():
                new_private_chat = private_chat_form.save()
                new_private_chat.participants.add(request.user)
                new_private_chat.participants.add(user)
                new_private_chat.save()
                return HttpResponseRedirect("/chat/{0}".format(new_private_chat.id))
            else:
                open_new_chat_form = True

    return render_to_response("django_project/profile.html",
                              {"self": logged_user == user,
                               "get_user": user,
                               "user_profile": user_profile,
                               "private_chats": private_chats,
                               "private_chat_form": private_chat_form,
                               "open_new_chat_form": open_new_chat_form},
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
