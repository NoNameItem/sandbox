import json
import random
import datetime

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

import huyaun_bot.bot_logic as bl
from huyaun_bot.models import Probability, LastWord, Exceptions, Timeout
import bots_common.utils as u


@csrf_exempt
def process_update(request):
    raw = request.body.decode('utf-8')
    r = json.loads(raw)

    print(r)

    try:
        chat_id = r['message']['chat']['id']
        message = r['message'].get('text')
    except KeyError:
        return JsonResponse({}, status=200)

    if message is None:
        return JsonResponse({}, status=200)

    # Стандартные триггеры
    reply = u.get_common_reply(message, bl.BOT.username)
    print('#{0}#'.format(reply))
    if reply:
        bl.TB.sendMessage(chat_id, reply)
        return JsonResponse({}, status=200)

    # Не хуефицировать последнее слово
    if message.upper() == '@HUYAUN_BOT ХУЙНЯ КАКАЯ-ТО':

        try:
            lw = LastWord.objects.get(chat_id=chat_id)
        except LastWord.DoesNotExist:
            # bl.TB.sendMessage(chat_id, random.choice(bl.NEGATIVE_RESPONSE))
            u.reply_no(bl.TB, chat_id)
            return JsonResponse({}, status=200)
        if datetime.datetime.now(datetime.timezone.utc) - lw.dt > datetime.timedelta(minutes=2) or r['message'][
            'from'].get('username', '').upper() != 'NONAMEITEM':
            # bl.TB.sendMessage(chat_id, random.choice(bl.NEGATIVE_RESPONSE))
            u.reply_no(bl.TB, chat_id)
        else:
            try:
                e = Exceptions.objects.get(key=lw.word)
                e.val = None
            except Exceptions.DoesNotExist:
                e = Exceptions(key=lw.word)
            e.save()
            # bl.TB.sendMessage(chat_id, random.choice(bl.POSITIVE_RESPONSE))
            u.reply_yes(bl.TB, chat_id)
        return JsonResponse({}, status=200)

    # Скорректировать последнее слово
    match = bl.CORRECT_REGEXP.match(message)
    if match:
        try:
            lw = LastWord.objects.get(chat_id=chat_id)
        except LastWord.DoesNotExist:
            # bl.TB.sendMessage(chat_id, random.choice(bl.NEGATIVE_RESPONSE))
            u.reply_no(bl.TB, chat_id)
            return JsonResponse({}, status=200)
        if datetime.datetime.now(datetime.timezone.utc) - lw.dt > datetime.timedelta(minutes=2) or \
                        r['message']['from'].get('username', '').upper() != 'NONAMEITEM' or match.group(1).upper()[
                                                                                            :2] != 'ХУ':
            # bl.TB.sendMessage(chat_id, random.choice(bl.NEGATIVE_RESPONSE))
            u.reply_no(bl.TB, chat_id)
        else:
            try:
                e = Exceptions.objects.get(key=lw.word)
                e.val = match.group(1).title()
            except Exceptions.DoesNotExist:
                e = Exceptions(key=lw.word, val=match.group(1).title())
            e.save()
            # bl.TB.sendMessage(chat_id, random.choice(bl.POSITIVE_RESPONSE))
            u.reply_yes(bl.TB, chat_id)
        return JsonResponse({}, status=200)

    # Изменение вероятности реакции
    match = bl.SET_PROBABILITY_REGEXP.match(message)
    if match:
        try:
            p = Probability.objects.get(chat_id=int(chat_id))
        except Probability.DoesNotExist:
            p = Probability(chat_id=int(chat_id))
        value = int(match.group('val'))
        if value <= 100:
            p.value = value
            p.save()
            # bl.TB.sendMessage(chat_id, random.choice(bl.POSITIVE_RESPONSE))
            u.reply_yes(bl.TB, chat_id)
        else:
            # bl.TB.sendMessage(chat_id, random.choice(bl.NEGATIVE_RESPONSE))
            u.reply_no(bl.TB, chat_id)
        return JsonResponse({}, status=200)

    # Изменение задержки
    match = bl.SET_TIMEOUT_REGEXP.match(message)
    if match:
        try:
            t = Timeout.objects.get(chat_id=int(chat_id))
        except Timeout.DoesNotExist:
            t = Timeout(chat_id=int(chat_id))
        try:
            value = int(match.group('val'))
            t.value = value
            t.save()
            # bl.TB.sendMessage(chat_id, random.choice(bl.POSITIVE_RESPONSE))
            u.reply_yes(bl.TB, chat_id)
        except Timeout.DoesNotExist:
            # bl.TB.sendMessage(chat_id, random.choice(bl.NEGATIVE_RESPONSE))
            u.reply_no(bl.TB, chat_id)
        return JsonResponse({}, status=200)

    # Остальные /-комманды
    if message.startswith('/'):
        u.reply_no(bl.TB, chat_id)

    # Просто хуефицируем остальное
    try:
        p = Probability.objects.get(chat_id=int(chat_id)).value
    except Probability.DoesNotExist:
        p = 100

    try:
        timeout = Timeout.objects.get(chat_id=int(chat_id)).value
    except Timeout.DoesNotExist:
        timeout = 20

    try:
        last_dt = LastWord.objects.get(chat_id=chat_id).dt
    except LastWord.DoesNotExist:
        last_dt = None

    if random.random() * 100 < p and (not last_dt or datetime.datetime.now(datetime.timezone.utc) - last_dt >
      datetime.timedelta(seconds=timeout)):

        reply = bl.operator(message, chat_id)

        if reply:
            bl.TB.sendMessage(chat_id, reply)
    return JsonResponse({}, status=200)
