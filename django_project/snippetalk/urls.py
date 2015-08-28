from django.conf.urls import patterns, url

__author__ = 'nonameitem'


urlpatterns = patterns('',
                       url(r'^$', 'snippetalk.views.recent'),
                       url(r'^my/$', 'snippetalk.views.my'),
                       url(r'^create/$', 'snippetalk.views.create'),
                       url(r'^(?P<snippet_id>\d+)/$', 'snippetalk.views.show')
                       )
