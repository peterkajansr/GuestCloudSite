from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('home.urls', namespace="home")),
    url(r'^', include('crm.urls', namespace="crm")),
    url(r'^admin/', include(admin.site.urls)),
)
