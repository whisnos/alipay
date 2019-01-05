# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-12-20 15:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0014_auto_20181217_1520'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderinfo',
            name='pay_status',
            field=models.CharField(choices=[('TRADE_SUCCESS', '支付成功'), ('TRADE_CLOSE', '支付关闭'), ('PAYING', '待支付')], default='PAYING', max_length=30, verbose_name='订单状态'),
        ),
    ]