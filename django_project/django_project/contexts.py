from django_project.settings import PROJECTS, WEBSOCKET_PREFIX, DEBUG


def dynamic_context(request):
    recent_chats = None
    if request.user.is_authenticated():
        recent_chats = request.user.chat_set.all().order_by('-last_message_time')[:5]
    return {'recent_chats': recent_chats}


def settings_context(request):
    return {'projects': sorted(PROJECTS, key=lambda x: x[1]),
            'WEBSOCKET_PREFIX': WEBSOCKET_PREFIX,
            'DEBUG': DEBUG}
