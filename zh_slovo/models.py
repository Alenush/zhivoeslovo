from django.db import models
# -*- coding: utf-8 -*-
#__author__ = 'alenush'
# Create your models here.

class Dict_text(models.Model):
    dic_origin_text = models.CharField(max_length=5000)
    text_number = models.IntegerField(default=0)


class Annotate_text(models.Model):
    id_of_word_error = models.IntegerField()
    words_of_text = models.CharField(max_length=100)
    text_number = models.IntegerField(default=0)

class Errors_in_text(models.Model):
    ORFO = 'OR'
    PUNKT = "PU"
    ERRORS = (
        (ORFO, u'Орфографическая ошибка'),
        (PUNKT, u'Пунктационная ошибка'),
    )
    id_of_word_error = models.IntegerField()
    accepted_variant = models.CharField(max_length=50)
    error_variant = models.CharField(max_length=50)
    comments_to_error = models.CharField(max_length=500)
    type_of_error = models.CharField(max_length=7, choices=ERRORS, default=ORFO)
    text_number = models.IntegerField(default=0)