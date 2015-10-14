# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zh_slovo', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dict_text',
            name='dic_user_text',
        ),
    ]
