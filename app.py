from __future__ import absolute_import

#  settings
import settings
from django.apps import AppConfig

#  views
from django.http import HttpResponse
def index(request):
    return HttpResponse("Hello World!")

#  urls
from django.conf.urls import patterns, url
from hours import views
urlpatterns = [
    url(r'^$', index),
    url(r'^billing', views.billing),
    url(r'^holidays', views.gcalholidays),
]

# "manage.py"
import sys
from django.core import management
from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
if __name__ == '__main__':
    management.execute_from_command_line(sys.argv)
