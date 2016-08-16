#  urls
from django.conf.urls import patterns, url
from views import index
from hours import views
from connector import views as cv
urlpatterns = [
    url(r'^$', index),
    url(r'^billing', views.billing),
    url(r'^holidays', views.gcalholidays),
    url(r'^report/(?P<name>[\w \-]+)', cv.report),
]
