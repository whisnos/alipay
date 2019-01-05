from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime, date
from time import strftime

# Create your models here.
class UserProfile(AbstractUser):
    '''
    用户名，邮箱，手机号
    提现方式，姓名，收款码，账号
    '''
    email = models.EmailField(max_length=50, null=True, blank=True, verbose_name='邮箱')
    mobile = models.CharField(max_length=11, null=True, blank=True, verbose_name='手机号')
    verify_info = models.CharField(max_length=20, null=True, blank=True, verbose_name='预留信息')
    # user_qq = models.CharField(max_length=20, null=True, blank=True, verbose_name='预留QQ')
    qq = models.CharField(max_length=20, null=True, blank=True, verbose_name='预留QQ')
    name = models.CharField(max_length=25, null=True, blank=True, verbose_name='姓名')
    account_num = models.CharField(max_length=35, null=True, blank=True, verbose_name='收款账号')
    receive_way = models.CharField(max_length=10, null=True, blank=True, choices=((0, '支付宝'), (1, '微信'), (2, '银行')),
                                   verbose_name='提现方式')
    bank_type = models.CharField(max_length=15, null=True, blank=True, verbose_name='银行类型')
    qr_code = models.ImageField(null=True, blank=True, verbose_name='二维码')
    uid = models.CharField(max_length=50, null=True, blank=True, verbose_name='用户uid')
    auth_code = models.CharField(max_length=32, null=True, blank=True, verbose_name='用户授权码')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='注册时间')
    notify_url = models.CharField(max_length=100, null=True, blank=True, verbose_name='商户回调url')
    total_money = models.FloatField(default=0.0, verbose_name='当前收款余额')
    service_rate = models.FloatField(default=0.02, verbose_name='提现费率')

    class Meta:
        verbose_name = '用户管理'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class NoticeInfo(models.Model):
    title = models.CharField(max_length=100, verbose_name='公告标题')
    content = models.TextField(verbose_name='公告内容')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='创建时间')

    class Meta:
        verbose_name = '公告管理'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title
