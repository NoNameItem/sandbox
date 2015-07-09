from django.conf.urls import patterns, include, url
from django.contrib import admin
from views import MyRegistrationView

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'django_project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/register/$', MyRegistrationView.as_view(), name='registration_register'),
    url(r'^accounts/', include('registration.backends.simple.urls')),
)
