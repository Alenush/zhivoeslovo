#__author__ = 'alenush'
from django.conf.urls import url
from django.conf.urls import *
from . import models
from . import views

urlpatterns = [

    url(r'^begin/$', views.begin_dict, name='begin_dict'),
    url(r'^ajax/results/$', views.count_results, name='result_dict'),
    url(r'^ajax/send_results/$', views.send_good_result, name="send_result"),
    url(r'^$', views.anons, name='anons'),
    url(r'^success/', views.success, name='success'),
    url(r'^test/', views.test, name='test_json'),
    url(r'^selftest/', views.selftest, name='selftest'),
]
