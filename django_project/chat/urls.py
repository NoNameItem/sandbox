from django.conf.urls import patterns, url

__author__ = 'nonameitem'

urlpatterns = patterns('',
                       url(r'^$', 'chat.views.show_chat_list'),
                       url(r'^new/$', 'chat.views.create_chat'),
                       url(r'^(?P<chat_id>\d+)/$', 'chat.views.show_chat'),
                       url(r'^post/(?P<chat_id>\d+)/$', 'chat.views.post'),
                       url(r'^add_users/(?P<chat_id>\d+)/$', 'chat.views.add_users'),
                       url(r'^leave/(?P<chat_id>\d+)/$', 'chat.views.leave'),
                       url(r'^change_topic/', 'chat.views.change_topic'),
                       url(r'^get_previous/(?P<chat_id>\d+)/$', 'chat.views.get_previous'),
                       url(r'^merge_private/(?P<user_id>\d+)/$', 'chat.views.merge_private'),
                       )
