# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-01-03 15:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0051_auto_20190103_1530'),
    ]

    operations = [
        migrations.AddField(
            model_name='withdrawmoney',
            name='receive_money_info',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='收款信息'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='pay_status',
            field=models.CharField(choices=[('TRADE_SUCCESS', '支付成功'), ('PAYING', '待支付'), ('TRADE_CLOSE', '支付关闭')], default='PAYING', max_length=30, verbose_name='订单状态'),
        ),
    ]
