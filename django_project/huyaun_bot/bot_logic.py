import datetime
import re

import telepot

import bots_common.utils as utils
from bots_common.models import Bot
from huyaun_bot.models import LastWord, Exceptions


BOT = Bot.objects.get(username='huyaun_bot')
TB = telepot.Bot(BOT.token)
TB.setWebhook('https://nonameitem.com/bot/huyet/{0}/'.format(BOT.token))

LAST_WORD_REGEXP = re.compile(r'([-а-яА-ЯёЁ]+)[^а-яА-Яa-zA-ZёЁ]*$')
BASE_REGEXP = re.compile(r'([АЕЁИОУЫЭЮЯ])([-А-ЯёЁ]*)')
SET_PROBABILITY_REGEXP = re.compile(r'^/p(?P<val>\d+)(@huyaun_bot)?')
SET_TIMEOUT_REGEXP = re.compile(r'^/to(?P<val>\d+)(@huyaun_bot)?')
CORRECT_REGEXP = re.compile(r'^@huyaun_bot скорее ([а-яА-Я]+)$')

VOWELS = {'А': 'я',
          'Е': 'е',
          'Ё': 'ё',
          'И': 'и',
          'О': 'е',
          'У': 'ю',
          'Ы': 'и',
          'Э': 'е',
          'Ю': 'ю',
          'Я': 'я'}

# TODO: Вынести в базу

NEGATIVE_RESPONSE = ['Попизди мне тут',
                     'Не, нихуя',
                     'Не выебывайся, плез',
                     'Нет',
                     'Хуй там плавал',
                     'Говна поешь']

POSITIVE_RESPONSE = ['Ну лан',
                     'Кк',
                     'Ок',
                     'Уговорил']

THANKS = ['СПАСИБО',
          'ИМЕННО',
          'СПС',
          'ОТ ДУШИ']

YOU_ARE_WELCOME = ['Нез',
                   'Всегда рад',
                   'Хуйня делов',
                   'Не за что']


def is_thanks(message):
    m = message.upper()
    if m.startswith('@HUYAUN_BOT'):
        for i in THANKS:
            if i in m:
                return True
    return False


def get_updates():
    offset = int(utils.get_parameter('LAST_UPDATE', BOT))
    updates = TB.getUpdates(offset=offset+1)
    if updates:
        utils.set_parameter('LAST_UPDATE', BOT, max(map(lambda x: x['update_id'], updates)))
    return updates


# Huefication operator
def operator(text, chat_id):
    match = LAST_WORD_REGEXP.search(text)
    try:
        lw = LastWord.objects.get(chat_id=chat_id)
    except LastWord.DoesNotExist:
        lw = LastWord(chat_id=chat_id)
    if match:
        word = match.group(1)
        print(word)
        print(word.upper())
        if word[1:].upper() == 'УЙ':
            lw.word = word.upper()
            lw.dt = datetime.datetime.now()
            lw.save()
            return 'Хуй'
        else:
            try:
                e = Exceptions.objects.get(key=word.upper())
                lw.word = word.upper()
                lw.dt = datetime.datetime.now()
                lw.save()
                if e.val:
                    return e.val.capitalize()
                else:
                    return None
            except Exceptions.DoesNotExist:
                base_match = BASE_REGEXP.search(word.upper())
                if base_match:
                    lw.word = word.upper()
                    lw.dt = datetime.datetime.now()
                    lw.save()
                    return "Ху{0}{1}".format(VOWELS[base_match.group(1)], base_match.group(2)).capitalize()
    else:
        return None
