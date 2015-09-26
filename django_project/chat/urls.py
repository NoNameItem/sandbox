from django.conf.urls import patterns, url

__author__ = 'nonameitem'

urlpatterns = patterns('',
                       url(r'^$', 'chat.views.show_chat_list', name='main'),
                       url(r'^new/$', 'chat.views.create_chat', name='new'),
                       url(r'^(?P<chat_id>\d+)/$', 'chat.views.show_chat', name='chat'),
                       url(r'^post/(?P<chat_id>\d+)/$', 'chat.views.post', name='post'),
                       url(r'^add_users/(?P<chat_id>\d+)/$', 'chat.views.add_users', name='add_users'),
                       url(r'^leave/(?P<chat_id>\d+)/$', 'chat.views.leave', name='leave'),
                       url(r'^change_topic/', 'chat.views.change_topic', name='change_topic'),
                       url(r'^get_previous/(?P<chat_id>\d+)/$', 'chat.views.get_previous', name='previous'),
                       url(r'^get_updates/(?P<chat_id>\d+)/$', 'chat.views.get_updates', name='updates'),
                       url(r'^merge_private/(?P<user_id>\d+)/$', 'chat.views.merge_private', name='merge_private'),
                       )
