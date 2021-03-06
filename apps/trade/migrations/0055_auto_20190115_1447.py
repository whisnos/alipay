# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-01-15 14:47
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0054_auto_20190115_1446'),
    ]

    operations = [
        migrations.CreateModel(
            name='WXBusinessInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='收款公司名称')),
                ('wx_mchid', models.CharField(max_length=32, verbose_name='商户号')),
                ('wx_appid', models.CharField(max_length=32, verbose_name='微信商家appid')),
                ('wxapi_key', models.TextField(verbose_name='微信key')),
                ('add_time', models.DateTimeField(default=datetime.datetime.now, verbose_name='创建时间')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否激活状态')),
                ('last_time', models.DateTimeField(blank=True, null=True, verbose_name='最后收款时间')),
                ('total_money', models.FloatField(default=0.0, verbose_name='总收款')),
            ],
            options={
                'verbose_name': '微信管理',
                'verbose_name_plural': '微信管理',
            },
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='pay_status',
            field=models.CharField(choices=[('TRADE_CLOSE', '支付关闭'), ('TRADE_SUCCESS', '支付成功'), ('PAYING', '待支付'), ('NOTICE_FAIL', '通知失败')], default='PAYING', max_length=30, verbose_name='订单状态'),
        ),
    ]
