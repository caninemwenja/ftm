from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('questions.urls')),
    url(r'^account/', include('registration.backends.simple.urls')),
    url(r'^account/', include('django.contrib.auth.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
