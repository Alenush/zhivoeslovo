# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zh_slovo', '0003_annotate_text_errors_in_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='annotate_text',
            name='text_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='dict_text',
            name='text_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='errors_in_text',
            name='text_number',
            field=models.IntegerField(default=0),
        ),
    ]
