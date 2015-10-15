#__author__ = 'alenush'
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^slovo/', views.choose_dict, name='choose_dict'),
    url(r'write_dict/', views.begin_dict, name='begin_dict'),
    url(r'results$', views.count_results, name='result_dict'),
]
