# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-12-26 21:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0038_auto_20181226_1854'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='withdrawmoney',
            name='money_flag',
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='pay_status',
            field=models.CharField(choices=[('TRADE_SUCCESS', '支付成功'), ('TRADE_CLOSE', '支付关闭'), ('PAYING', '待支付')], default='PAYING', max_length=30, verbose_name='订单状态'),
        ),
    ]
