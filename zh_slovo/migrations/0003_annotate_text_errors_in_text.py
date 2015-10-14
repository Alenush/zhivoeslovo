# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zh_slovo', '0002_remove_dict_text_dic_user_text'),
    ]

    operations = [
        migrations.CreateModel(
            name='Annotate_text',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('id_of_word_error', models.IntegerField()),
                ('words_of_text', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Errors_in_text',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('id_of_word_error', models.IntegerField()),
                ('accepted_variant', models.CharField(max_length=50)),
                ('error_variant', models.CharField(max_length=50)),
                ('comments_to_error', models.CharField(max_length=500)),
                ('type_of_error', models.CharField(default=b'OR', max_length=7, choices=[(b'OR', '\u041e\u0440\u0444\u043e\u0433\u0440\u0430\u0444\u0438\u0447\u0435\u0441\u043a\u0430\u044f \u043e\u0448\u0438\u0431\u043a\u0430'), (b'PU', '\u041f\u0443\u043d\u043a\u0442\u0430\u0446\u0438\u043e\u043d\u043d\u0430\u044f \u043e\u0448\u0438\u0431\u043a\u0430')])),
            ],
        ),
    ]
