#__author__ = 'alenush'
from django.conf.urls import url
from django.conf.urls import *
from . import models
from . import views

urlpatterns = [
    url(r'^ajax/', views.begin_dict, name='begin_dict'),
    url(r'^results$', views.count_results, name='result_dict'),
    url(r'^send_results$', views.send_good_result, name="send_result")
]
