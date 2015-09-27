from chat.models import Chat

__author__ = 'nonameitem'


def get_private_chats(user1, user2):
    chats = Chat.objects.all()
    private_chats = []
    for chat in chats:
        if user1 in chat.participants.all() and user2 in chat.participants.all() and chat.participants.count() == 2:
            private_chats.append(chat)
    return private_chats


def get_chats_without_user(r_user, user):
    chats = Chat.objects.all()
    result = []
    for chat in chats:
        if r_user in chat.participants.all() and user not in chat.participants.all():
            result.append(chat)
    return result
