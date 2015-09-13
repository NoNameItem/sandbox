from django.conf.urls import patterns, url

__author__ = 'nonameitem'

urlpatterns = patterns('',
                       url(r'^$', 'snippetalk.views.recent', name='recent'),
                       url(r'^my/$', 'snippetalk.views.my', name='my'),
                       url(r'^create/$', 'snippetalk.views.show', name='create'),
                       url(r'^(?P<snippet_id>\d+)/$', 'snippetalk.views.show', name='snippet'),
                       url(r'^highlight/$', 'snippetalk.views.get_highlight', name='get_highlight'),
                       url(r'^save/$', 'snippetalk.views.save', name='save'),
                       url(r'^delete/(?P<snippet_id>\d+)/$', 'snippetalk.views.delete', name='delete'),
                       url(r'^fork/(?P<snippet_id>\d+)/$', 'snippetalk.views.show', {'fork': True}, name='fork'),
                       url(r'^comment/$', 'snippetalk.views.comment', name='comment'),
                       url(r'^download/(?P<snippet_id>\d+)/$', 'snippetalk.views.download', name='download'),
                       url(r'^upload/$', 'snippetalk.views.upload', name='upload'),
                       )
