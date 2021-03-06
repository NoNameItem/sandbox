import json
import datetime
import re

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, JsonResponse, Http404, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
import pika

from chat.models import Chat, Message, update_last_message
from chat.forms import ChatForm, get_merge_form


# url regex from http://daringfireball.net/2010/07/improved_regex_for_matching_urls
URL_REGEX = re.compile(r'''(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s\
()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''')


def wrap_links(text):
    return URL_REGEX.sub(lambda x: '<a href="{0}">{0}</a>'.format(x.group(0)), text)


@login_required
def show_chat_list(request):
    chats = Chat.objects.filter(participants=request.user).order_by('-last_message_time')
    return render_to_response('chat/chat_list.html',
                              {'chats': chats,
                               'active_page': 'all'},
                              RequestContext(request))


@login_required
def create_chat(request):
    if request.method == 'POST':
        form = ChatForm(request.POST)
        if form.is_valid():
            chat = form.save()
            if request.user not in chat.participants.all():
                chat.participants.add(request.user)
            mess = {
                'id': chat.id,
                'name': chat.name,
                'text': chat.topic,
                'sender': request.user.username,
                'link': reverse('chat:chat', kwargs={'chat_id': chat.id})
            }
            for user in chat.get_user_list():
                post_to_notify_queue(str(user.id), json.dumps({
                    'type': "C",
                    'mess': mess
                }))
            return HttpResponseRedirect(reverse('chat:chat', kwargs={'chat_id': chat.id}))
    else:
        form = ChatForm()
    return render_to_response('chat/create_chat.html',
                              {'form': form,
                               'active_page': 'create'},
                              RequestContext(request))


@login_required
def show_chat(request, chat_id):
    message_blocks = None
    not_all = False
    oldest_datetime = datetime.datetime.now()
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user not in chat.participants.all():
        raise PermissionDenied
    participants = chat.participants.all()
    potential_participants = User.objects.exclude(id__in=participants.distinct())

    messages = chat.message_set.all().order_by('-datetime')[:100]
    if messages.count() > 0:
        first_message = chat.message_set.order_by('datetime')[0]
        not_all, oldest_datetime, message_blocks = make_message_blocks(first_message, messages)

    return render_to_response('chat/show_chat.html',
                              {'chat': chat,
                               'message_blocks': message_blocks,
                               'potential_participants': potential_participants.order_by('username'),
                               'not_all': not_all,
                               'oldest_datetime': oldest_datetime.timestamp(),
                               'newest_datetime': datetime.datetime.now().timestamp()},
                              RequestContext(request))


def make_message_blocks(first_message, messages):
    message_blocks = []
    not_all = False
    oldest_datetime = None

    if messages.count() > 0:
        message_block = dict({'sender': messages[0].sender.username,
                              'photo': messages[0].sender.userprofile.image_url,
                              'messages': []})
        oldest_message = messages[messages.count() - 1]
        not_all = oldest_message != first_message
        oldest_datetime = oldest_message.datetime
        for message in messages:
            if message.sender.username == message_block['sender']:
                message_block['messages'].insert(0, message.text)
            else:
                message_blocks.insert(0, message_block)
                message_block = {'sender': message.sender.username,
                                 'photo': message.sender.userprofile.image_url,
                                 'messages': [message.text]}
        message_blocks.insert(0, message_block)
    return not_all, oldest_datetime, message_blocks


@login_required
def post(request, chat_id):
    if request.method == 'POST':
        chat = get_object_or_404(Chat, id=chat_id)

        if request.user not in chat.participants.all():
            raise PermissionDenied

        message = Message()
        message.text = wrap_links(request.POST['message'])
        message.sender = request.user
        message.thread = chat
        message.save()
        update_last_message(message)

        post_to_chat_queue(chat_id, message.get_json_string())
        mess = {
            'id': chat.id,
            'name': chat.name,
            'text': message.text,
            'sender': request.user.username,
            'link': reverse('chat:chat', kwargs={'chat_id': chat.id})
        }
        for user in chat.participants.all():
            post_to_notify_queue(str(user.id), json.dumps({
                'type': 'M',
                'mess': mess
            }))

        return JsonResponse(status=200, data={'result': True})

    else:
        return JsonResponse(status=400, data={'result': False})


# TODO: Refactor to one function
def post_to_chat_queue(chat_id, message):
    conn = pika.BlockingConnection(pika.ConnectionParameters('127.0.0.1'))
    channel = conn.channel()
    channel.exchange_declare(exchange='chat',
                             type='direct')
    channel.basic_publish(exchange='chat',
                          routing_key=chat_id,
                          body=message.encode('utf8'))


def post_to_notify_queue(user_id, message):
    conn = pika.BlockingConnection(pika.ConnectionParameters('127.0.0.1'))
    channel = conn.channel()
    channel.exchange_declare(exchange='notify',
                             type='direct')
    channel.basic_publish(exchange='notify',
                          routing_key=user_id,
                          body=message.encode('utf8'))


@login_required
def add_users(request, chat_id):
    if request.method == 'POST':
        chat = get_object_or_404(Chat, id=chat_id)
        if request.user not in chat.participants.all():
            raise PermissionDenied

        ids = json.loads(request.POST['selected'])
        for user_id in ids:
            user = get_object_or_404(User, id=user_id)
            chat.participants.add(user)
            mess = {
                'id': chat.id,
                'name': chat.name,
                'text': None,
                'sender': request.user.username,
                'link': reverse('chat:chat', kwargs={'chat_id': chat.id})
            }
            post_to_notify_queue(str(user.id), json.dumps({
                'type': 'I',
                'mess': mess
            }))
        data = get_user_lists(chat)
        post_to_chat_queue(chat_id, json.dumps(data))

        return JsonResponse(status=200, data={'message': "OK"})
    else:
        return JsonResponse(status=400, data={'message': "Please use POST"})


def get_user_lists(chat):
    participants = chat.participants.all()
    potential_participants = User.objects.exclude(id__in=participants.distinct())
    participants_out = []
    for participant in participants:
        participants_out.append(participant.username)
    participants_out.sort()
    potential_participants_out = []
    for participant in potential_participants:
        potential_participants_out.append((participant.id, participant.username))
    potential_participants_out.sort(key=lambda x: x[1])
    data = {'type': 'U',
            'participants': participants_out,
            'potential_participants': potential_participants_out}
    print(json.dumps(data))
    return data


@login_required
def leave(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user not in chat.participants.all():
        raise PermissionDenied
    chat.participants.remove(request.user)
    if len(chat.participants.all()) > 0:
        data = get_user_lists(chat)
        post_to_chat_queue(chat_id, json.dumps(data))
    else:
        chat.delete()
    return HttpResponseRedirect(reverse('chat:main'))


@login_required
def change_topic(request):
    if request.method == 'POST':
        try:
            chat = Chat.objects.get(id=request.POST['pk'])
        except Chat.DoesNotExist:
            return HttpResponse("Chat not found", status=404)
        if request.user not in chat.participants.all():
            raise PermissionDenied
        chat.topic = request.POST['value']
        chat.save()
        data = {'type': 'T',
                'topic': chat.topic}
        post_to_chat_queue(str(chat.id), json.dumps(data))
        mess = {
            'id': chat.id,
            'name': chat.name,
            'text': chat.topic,
            'sender': request.user.username,
            'link': reverse('chat:chat', kwargs={'chat_id': chat.id})
        }
        for user in chat.get_user_list():
            post_to_notify_queue(str(user.id), json.dumps({
                'type': "T",
                'mess': mess
            }))
        return HttpResponse(status=200)
    else:
        return HttpResponse("Bad request", status=400)


@login_required
def get_previous(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user not in chat.participants.all():
        raise PermissionDenied

    if request.method == 'GET':
        oldest_datetime = datetime.datetime.fromtimestamp(float(request.GET['oldest']))
        first_message = chat.message_set.order_by('datetime')[0]
        messages = chat.message_set.filter(datetime__lt=oldest_datetime).order_by('-datetime')[:100]

        not_all, oldest_datetime, message_blocks = make_message_blocks(first_message, messages)

        return JsonResponse(status=200, data={'not_all': not_all,
                                              'oldest_datetime': oldest_datetime.timestamp(),
                                              'message_blocks': message_blocks})
    else:
        return JsonResponse(status=400, data={'message': "Please use GET"})


@login_required
def merge_private(request, user_id):
    user = request.user
    other = get_object_or_404(User, id=user_id)
    form_class = get_merge_form(user, other)
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            new_chat = Chat()
            new_chat.name = form.cleaned_data['new_title']
            new_chat.topic = form.cleaned_data['new_topic']
            new_chat.save()
            new_chat.participants.add(user)
            new_chat.participants.add(other)
            chats = form.cleaned_data['chats']
            messages = Message.objects.none()
            for chat in chats:
                messages = messages | chat.message_set.all()
            messages = messages.order_by('datetime')
            for message in messages:
                message.thread = new_chat
                message.save()
            new_chat.save()
            for chat in chats:
                chat.delete()
            return HttpResponseRedirect(reverse('chat:chat', kwargs={'chat_id': new_chat.id}))
    else:
        form = form_class()
    return render_to_response('chat/merge_private.html',
                              {'form': form,
                               'other': other.username},
                              RequestContext(request))


@login_required
def get_updates(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user not in chat.participants.all():
        raise PermissionDenied
    if request.method == 'GET':
        newest_datetime = datetime.datetime.fromtimestamp(float(request.GET['newest']))
        first_message = chat.message_set.order_by('datetime')[0]
        messages = chat.message_set.filter(datetime__gt=newest_datetime).order_by('-datetime')

        not_all, oldest_datetime, message_blocks = make_message_blocks(first_message, messages)
        return JsonResponse(status=200, data={'newest_datetime': datetime.datetime.now().timestamp(),
                                              'message_blocks': message_blocks})
    else:
        return JsonResponse(status=400, data={'message': "Please use GET"})


def add_user(request, chat_id):
    if request.method == 'POST':
        try:
            chat = Chat.objects.get(id=int(chat_id))
            if request.user not in chat.participants.all():
                raise PermissionDenied
            user_id = request.POST['user_id']
            user = User.objects.get(id=int(user_id))
            chat.participants.add(user)
            data = get_user_lists(chat)
            post_to_chat_queue(chat_id, json.dumps(data))
            mess = {
                'id': chat.id,
                'name': chat.name,
                'text': None,
                'sender': request.user.username,
                'link': reverse('chat:chat', kwargs={'chat_id': chat.id})
            }
            post_to_notify_queue(str(user.id), json.dumps({
                'type': 'I',
                'mess': mess
            }))
        except Chat.DoesNotExist:
            return JsonResponse(status=404, data={'message': "Chat not found"})
        except User.DoesNotExist:
            return JsonResponse(status=404, data={'message': "User not found"})
        return JsonResponse(status=200, data={'message': "OK"})
    else:
        return JsonResponse(status=400, data={'message': "Please use POST"})
