# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-12-22 18:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0023_auto_20181222_1832'),
    ]

    operations = [
        migrations.AddField(
            model_name='withdrawmoney',
            name='full_name',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='姓名'),
        ),
    ]
