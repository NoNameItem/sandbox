from django.conf.urls import patterns, include, url

urlpatterns = [
    url(r'^huyet/', include('huyaun_bot.urls')),

    url(r'^common_responces/$', 'bots_common.views.common_responces'),
]