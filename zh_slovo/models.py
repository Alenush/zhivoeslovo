#!/usr/bin/env python
# -*- coding: utf-8 -*-
#__author__ = 'alenush'
import datetime
from django.db import models

class Dict_text(models.Model):
    dic_origin_text = models.CharField(max_length=5000)
    video_link = models.URLField()
    data = models.DateTimeField(auto_now_add=True)
    dict_name = models.CharField(max_length=100)


class Errors_table(models.Model):
    ORFO = 'OR'
    PUNKT = "PU"
    ERRORS = (
        (ORFO, u'Орфографическая ошибка'),
        (PUNKT, u'Пунктационная ошибка'),
    )
    id_dict = models.IntegerField() #link to dict_id
    symbol_place_in_sent = models.IntegerField()
    token_border_begin = models.IntegerField()
    token_border_end = models.IntegerField()
    comments_to_error = models.CharField(max_length=500)
    type_of_error = models.CharField(max_length=7, choices=ERRORS, default=ORFO)
    right_answer = models.CharField(max_length=100) #заголовок


class Answer_user(models.Model):
    MASC = 'M'
    FEM = "F"
    SEX = (
        (MASC, u'Мужчина'),
        (FEM, u'Женщина'),
    )
    dict_id = models.IntegerField() #link to dict_id
    user_text = models.CharField(max_length=500)
    username = models.CharField(max_length=100)
    id_hash = models.CharField(max_length=200)
    email = models.EmailField()
    age = models.IntegerField()
    sex = models.CharField(max_length=7, choices=SEX, default=MASC)
    city = models.CharField(max_length=50)
