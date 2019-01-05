# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-12-22 18:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0020_withdrawmoney_withdraw_no'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderinfo',
            name='pay_status',
            field=models.CharField(choices=[('TRADE_CLOSE', '支付关闭'), ('PAYING', '待支付'), ('TRADE_SUCCESS', '支付成功')], default='PAYING', max_length=30, verbose_name='订单状态'),
        ),
        migrations.AlterField(
            model_name='withdrawmoney',
            name='receive_way',
            field=models.CharField(choices=[('ALIPAY', '支付宝'), ('WECHAT', '微信'), ('BANK', '银行')], max_length=20, verbose_name='提现方式'),
        ),
        migrations.AlterField(
            model_name='withdrawmoney',
            name='withdraw_status',
            field=models.CharField(blank=True, choices=[('WITHING', '提现中'), ('SUCCESS', '提现成功'), ('FAIL', '提现失败')], max_length=20, null=True),
        ),
    ]