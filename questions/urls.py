from django.conf.urls import patterns, url


urlpatterns = patterns(
    '',
    url(r'^$', 'questions.views.home', name='home'),
    url(r'^users/\w+/', 'questions.views.home', name='home'),
    url(r'^questions/add/$', 'questions.views.add_question', name='questions.add'),
    url(r'^questions/edit/(\d+)/$', 'questions.views.edit_question', name='questions.edit'),
    url(r'^questions/remove/(\d+)/$', 'questions.views.remove_question', name='questions.remove'),
    url(r'^questions/publish/(\d+)/$', 'questions.views.publish_question', name='questions.publish'),
    url(r'^questions/scheme/(\d+)/$', 'questions.views.marking_scheme', name='questions.scheme'),
    url(r'^questions/scheme/add/(\d+)/$', 'questions.views.add_marking_answer', name='scheme.add'),
    url(r'^scheme/edit/(\d+)/$', 'questions.views.edit_marking_answer', name='scheme.edit'),
    url(r'^scheme/remove/(\d+)/$', 'questions.views.remove_marking_answer', name='scheme.remove'),
)
