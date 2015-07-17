from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
import django_project.settings as settings
import django_project.views as views

urlpatterns = patterns('',
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^accounts/register/$', views.MyRegistrationView.as_view(), name='registration_register'),
                       url(r'^accounts/profile/$', 'django_project.views.my_profile'),
                       url(r'^accounts/', include('registration.backends.simple.urls')),
                       url(r'^chat/', include('chat.urls')),

                       url(r'^$', 'django_project.views.home', name='home'),
                       url(r'^user/(?P<username>\w+)/$', views.profile),
                       url(r'^change_photo/(?P<user_id>\d+)/$', views.change_photo),
                       url(r'^change_profile/(?P<user_id>\d+)/$', views.change_profile),
                       )

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
