from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime, date

# Create your models here.
class UserProfile(AbstractUser):
	'''
	用户名，邮箱，手机号
	提现方式，姓名，收款码，账号
	'''
	email = models.EmailField(max_length=50, null=True, blank=True, verbose_name='邮箱')
	mobile = models.CharField(max_length=11, null=True, blank=True, verbose_name='手机号')
	verify_info = models.CharField(max_length=20, null=True, blank=True, verbose_name='预留信息')
	name = models.CharField(max_length=25, null=True, blank=True, verbose_name='姓名')
	account_num = models.CharField(max_length=35, null=True, blank=True, verbose_name='收款账号')
	receive_way = models.CharField(max_length=10, null=True, blank=True, choices=((0, '支付宝'), (1, '微信'), (2, '银行')),
								   verbose_name='提现方式')
	bank_type = models.CharField(max_length=15, null=True, blank=True, verbose_name='银行类型')
	qr_code = models.ImageField(null=True, blank=True, verbose_name='二维码')

	add_time = models.DateTimeField(default=datetime.now,verbose_name='注册时间')
	class Meta:
		verbose_name = '用户表'
		verbose_name_plural = verbose_name

	def __str__(self):
		return self.username
