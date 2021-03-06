# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-12-21 19:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0017_auto_20181220_1806'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderinfo',
            name='order_id',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='商户订单号'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='pay_status',
            field=models.CharField(choices=[('TRADE_CLOSE', '支付关闭'), ('TRADE_SUCCESS', '支付成功'), ('PAYING', '待支付')], default='PAYING', max_length=30, verbose_name='订单状态'),
        ),
    ]
