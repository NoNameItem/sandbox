from django_project.settings import PROJECTS, WEBSOCKET_PREFIX


def my_context(request):
    recent_chats = None
    if request.user.is_authenticated():
        recent_chats = request.user.chat_set.all().order_by('-last_message_time')[:5]
    return {'projects': sorted(PROJECTS, key=lambda x: x[1]),
            'recent_chats': recent_chats,
            'WEBSOCKET_PREFIX': WEBSOCKET_PREFIX}
