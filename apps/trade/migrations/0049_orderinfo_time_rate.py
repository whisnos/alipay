# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-01-03 14:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0048_auto_20190102_1820'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderinfo',
            name='time_rate',
            field=models.FloatField(blank=True, null=True, verbose_name='当时费率'),
        ),
    ]
