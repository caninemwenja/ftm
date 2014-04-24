from django.conf.urls import patterns, url


urlpatterns = patterns(
    '',
    url(r'^$', 'questions.views.home', name='home'),
)
