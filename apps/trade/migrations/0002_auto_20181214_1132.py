# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-12-14 11:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderinfo',
            name='pay_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='支付时间'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='pay_status',
            field=models.CharField(choices=[('PAYING', '待支付'), ('TRADE_SUCCESS', '支付成功'), ('TRADE_FINSHED', '交易结束'), ('TRADE_CLOSE', '支付关闭'), ('TRADE_FAIL', '支付失败')], default='PAYING', max_length=30, verbose_name='订单状态'),
        ),
    ]