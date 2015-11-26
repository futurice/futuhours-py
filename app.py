from __future__ import absolute_import
from djangomi.init import *
ROOT = os.path.dirname(os.path.realpath(__file__))
settings.ROOT_URLCONF = "app"
settings.TEMPLATE_DIRS = (
    os.path.join(ROOT, 'templates'),
)
settings.INSTALLED_APPS += [
'django.contrib.contenttypes',
'django.contrib.auth',
'django.contrib.admin',
'django.contrib.sessions',
'hours',
'bootstrapform',
]

from django.apps import AppConfig

def index(request):
    return HttpResponse("Hello World!")

from hours import views

urlpatterns = [
    url(r'^$', index),
    url(r'^billing', views.billing),
]

app = get_wsgi_application()
if __name__ == '__main__':
    management.execute_from_command_line(sys.argv)
