import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, JsonResponse, Http404, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

import pika

from chat.models import Chat, Message, update_last_message
from chat.forms import ChatForm


@login_required
def show_chat_list(request):
    chats = Chat.objects.filter(participants=request.user).order_by('-last_message_time')
    return render_to_response('chat/chat_list.html',
                              {'chats': chats},
                              RequestContext(request))


@login_required
def create_chat(request):
    if request.method == 'POST':
        form = ChatForm(request.POST)
        if form.is_valid():
            chat = form.save()
            if request.user not in chat.participants.all():
                chat.participants.add(request.user)
            return HttpResponseRedirect('/chat/')
    else:
        form = ChatForm()
    return render_to_response('chat/create_chat.html',
                              {'form': form},
                              RequestContext(request))


@login_required
def show_chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user not in chat.participants.all():
        raise PermissionDenied
    participants = chat.participants.all()
    potential_participants = User.objects.exclude(id__in=participants.distinct())

    messages = chat.message_set.order_by('-datetime')[:100]
    message_blocks = []
    if len(messages) > 0:
        sender = messages[0].sender
        message_block = []
        for message in messages:
            if message.sender == sender:
                # message_block.append(message.text)
                message_block.insert(0, message.text)
            else:
                message_blocks.insert(0, (sender, message_block))
                sender = message.sender
                message_block = [message.text]
        message_blocks.insert(0, (sender, message_block))

    return render_to_response('chat/show_chat.html',
                              {'chat': chat,
                               'message_blocks': message_blocks,
                               'potential_participants': potential_participants.order_by('username')},
                              RequestContext(request))


@login_required
def post(request, chat_id):
    if request.method == 'POST':
        chat = get_object_or_404(Chat, id=chat_id)

        if request.user not in chat.participants.all():
            raise PermissionDenied

        message = Message()
        message.text = request.POST['message']
        message.sender = request.user
        message.thread = chat
        message.save()
        update_last_message(message)

        post_to_queue(chat_id, message.get_json_string())

        return JsonResponse(status=200, data={'result': True})

    else:
        return JsonResponse(status=400, data={'result': False})


def post_to_queue(chat_id, message):
    conn = pika.BlockingConnection(pika.ConnectionParameters('127.0.0.1'))
    channel = conn.channel()
    channel.exchange_declare(exchange='chat',
                             type='direct')
    channel.basic_publish(exchange='chat',
                          routing_key=chat_id,
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
        data = get_user_lists(chat)
        post_to_queue(chat_id, json.dumps(data))

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
    data = get_user_lists(chat)
    post_to_queue(chat_id, json.dumps(data))
    return HttpResponseRedirect('/chat/')


@login_required
def change_topic(request):
    if request.method == 'POST':
        try:
            chat = Chat.objects.get(id=request.POST['pk'])
        except Chat.DoesNotExist:
            return HttpResponse(status=404)
        if request.user not in chat.participants.all():
            raise PermissionDenied
        chat.topic = request.POST['value']
        chat.save()
        data = {'type': 'T',
                'topic': chat.topic}
        post_to_queue(str(chat.id), json.dumps(data))
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=400)
