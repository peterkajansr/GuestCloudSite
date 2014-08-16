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
    ])), 
)