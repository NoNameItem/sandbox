from django.conf.urls import patterns, url

__author__ = 'nonameitem'

urlpatterns = patterns('',
                       url(r'^$', 'snippetalk.views.recent'),
                       url(r'^my/$', 'snippetalk.views.my'),
                       url(r'^create/$', 'snippetalk.views.show'),
                       url(r'^(?P<snippet_id>\d+)/$', 'snippetalk.views.show'),
                       url(r'^highlight/$', 'snippetalk.views.get_highlight'),
                       url(r'^save/$', 'snippetalk.views.save'),
                       url(r'^delete/(?P<snippet_id>\d+)/$', 'snippetalk.views.delete'),
                       url(r'^fork/(?P<snippet_id>\d+)/$', 'snippetalk.views.show', {'fork': True}),
                       url(r'^comment/$', 'snippetalk.views.comment'),
                       url(r'^download/(?P<snippet_id>\d+)/$', 'snippetalk.views.download'),
                       url(r'^upload/$', 'snippetalk.views.upload'),
                       )
