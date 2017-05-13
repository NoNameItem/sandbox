from django.conf.urls import patterns, include, url

import huyaun_bot.bot_logic as bl
import huyaun_bot.views as views

urlpatterns = [
    url('^{0}'.format(bl.BOT.token), views.process_update)
]