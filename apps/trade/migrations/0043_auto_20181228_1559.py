# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-12-28 15:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0042_auto_20181228_1556'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderinfo',
            name='pay_status',
            field=models.CharField(choices=[('PAYING', '待支付'), ('TRADE_SUCCESS', '支付成功'), ('TRADE_CLOSE', '支付关闭')], default='PAYING', max_length=30, verbose_name='订单状态'),
        ),
    ]
