import random

from bots_common.models import Bot, Parameter, CommonTriggers, CommonReactions


# Get bot id by telegram username
def get_bot_id(username):
    return Bot.objects.get(username=username).id


# Get parameter value
def get_parameter(code, bot):
    return Parameter.objects.filter(code=code.upper()).get(bot=bot).value


def set_parameter(code, bot, value):
    p = Parameter.objects.filter(code=code.upper()).get(bot=bot)
    p.value = value
    p.save()


def get_random_record(qs):
    records = list(qs)
    return random.choice(records)


def reply_yes(tb, chat_id):
    tb.sendMessage(chat_id, get_random_record(CommonReactions.objects.filter(trigger_type='YES')).response)


def reply_no(tb, chat_id):
    tb.sendMessage(chat_id, get_random_record(CommonReactions.objects.filter(trigger_type='NO')).response)


def get_common_reply(message, bot_username):
    print(message)
    if message and message.startswith('@{0}'.format(bot_username)):
        u_message = message.upper()
        triggered_types = set()
        for trigger in CommonTriggers.objects.all().iterator():
            if trigger.trigger in u_message:
                triggered_types.add(trigger.type)
        if triggered_types:
            responses = []
            for trigger_type in triggered_types:
                responses.append(get_random_record(CommonReactions.objects.filter(trigger_type=trigger_type)).response)
            return random.choice(responses)
    return None
