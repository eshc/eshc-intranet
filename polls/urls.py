from django.conf.urls import url
from . import views

app_name = 'polls'

urlpatterns = [
		url(r'^$', views.index, name='index'),
		url(r'^submit/$', views.submit, name='submit'),
	    url(r'^(?P<pk>[0-9]+)/delete/$', views.delete, name='delete'),
	    url(r'^(?P<pk>[0-9]+)/$', views.detail, name='detail'),
	]
