from django.conf.urls import patterns, url, include
# from django.contrib import auth
from crm import views

urlpatterns = patterns('',
    url(r'^profiles/$', views.profile_redirect, name='profile_redirect'),
    url(r'^accounts/', include('django.contrib.auth.urls', namespace='auth')),
    url(r'^register/', views.register, name='register'),
    url(r'^p/(?P<username>[^/]*)/', include([
        url(r'^$', views.profile_home, name='profile_home'),
        url(r'^guestflow/$', views.guestflow, name='guestflow'),
        url(r'^import/$', views.import_guest, name='import'),
        url(r'^guests/$', views.guests, name='guests'),
        url(r'^guest/(?P<guest_id>\d+)/$', views.guest_detail, name='guest_detail'),
        url(r'^invite/$', views.invitations, name='invitations'),
        url(r'^mail/create/$', views.invitation_create, name='invitation_create'),
        url(r'^mail/(?P<invitation_id>\d+)/$', views.invitation_edit, name='invitation_edit'),
        url(r'^mail/(?P<invitation_id>\d+)/preview/$', views.invitation_preview, name='invitation_preview'),
    ])), 
)