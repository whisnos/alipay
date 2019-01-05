# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-12-25 17:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0013_userprofile_notify_url'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userprofile',
            options={'verbose_name': '用户管理', 'verbose_name_plural': '用户管理'},
        ),
        migrations.AddField(
            model_name='userprofile',
            name='total_money',
            field=models.FloatField(blank=True, null=True, verbose_name='用户总收款'),
        ),
    ]