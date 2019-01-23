from django.db import models
from user.models import UserProfile
from datetime import datetime


# Create your models here.
class OrderInfo(models.Model):
    PAY_STATUS = {
        ('PAYING', '待支付'),
        ('TRADE_SUCCESS', '支付成功'),
        ('TRADE_CLOSE', '支付关闭'),
        ('NOTICE_FAIL', '通知失败'),
    }
    # 用户
    user = models.ForeignKey(UserProfile, verbose_name='用户')
    # 支付状态
    pay_status = models.CharField(default='PAYING', max_length=30, choices=PAY_STATUS, verbose_name='订单状态')
    # 总金额
    total_amount = models.FloatField(verbose_name='总金额')
    # 订单号
    order_no = models.CharField(max_length=100, unique=True, verbose_name='网站订单号')
    # 交易号
    trade_no = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name='支付宝交易号')
    # 留言
    user_msg = models.CharField(max_length=200, null=True, blank=True, verbose_name='用户留言')
    # 支付时间
    pay_time = models.DateTimeField(null=True, blank=True, verbose_name="支付时间")
    # 创建时间
    add_time = models.DateTimeField(default=datetime.now, verbose_name='创建时间')
    order_id = models.CharField(max_length=100, null=True, blank=True, verbose_name='商户订单号')
    # 支付类型
    receive_way = models.CharField(max_length=20, choices=(('ALIPAY', '支付宝'), ('WECHAT', '微信'), ('BANK', '银行')),
                                   verbose_name='支付类型', default='ALIPAY')
    pay_url = models.TextField(null=True, blank=True, verbose_name='支付链接')

    # plat_type = models.CharField(null=True,blank=True,max_length=10,verbose_name='平台类型')

    # time_rate = models.FloatField(null=True,blank=True, verbose_name='当时费率')

    def __str__(self):
        return str(self.order_no)

    class Meta:
        verbose_name = '订单管理'
        verbose_name_plural = verbose_name


class WithDrawMoney(models.Model):
    user = models.ForeignKey(UserProfile, verbose_name='用户')
    money = models.FloatField(verbose_name='提现金额')
    real_money = models.FloatField(null=True, blank=True, verbose_name='实际到账金额')
    receive_way = models.CharField(max_length=20, choices=(('ALIPAY', '支付宝'), ('WECHAT', '微信'), ('BANK', '银行')),
                                   verbose_name='提现类型')
    bank_type = models.CharField(max_length=15, null=True, blank=True, verbose_name='银行类型')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='提现时间')
    withdraw_status = models.CharField(max_length=20,
                                       choices=(('0', '处理中'), ('1', '已处理')),
                                       default='0', verbose_name='提现状态')
    withdraw_no = models.CharField(max_length=50, unique=True, verbose_name='提现单号', null=True, blank=True)
    # 留言
    user_msg = models.CharField(max_length=200, null=True, blank=True, verbose_name='用户留言')
    receive_account = models.CharField(max_length=50, null=True, blank=True, verbose_name='账号')
    receive_time = models.DateTimeField(null=True, blank=True, verbose_name='到账时间')
    full_name = models.CharField(max_length=20, null=True, blank=True, verbose_name='姓名')
    freeze_money = models.FloatField(default=0.0, verbose_name='冻结金额')
    default_flag = models.BooleanField(default=False, verbose_name='旗帜')
    time_rate = models.FloatField(null=True, blank=True, verbose_name='当时费率')
    open_bank = models.CharField(max_length=50, null=True, blank=True, verbose_name='开户行')
    receive_money_info = models.CharField(max_length=200, null=True, blank=True, verbose_name='收款信息')

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = '提现管理'
        verbose_name_plural = verbose_name


class BusinessInfo(models.Model):
    '''
    商家公司名
    商家支付宝appid
    商家支付宝公钥
    商家支付宝私钥
    创建时间
    是否激活
    最后收款时间
    '''
    name = models.CharField(max_length=50, verbose_name='收款公司名称')
    c_appid = models.CharField(max_length=32, verbose_name='商家支付宝appid')
    alipay_public_key = models.TextField(verbose_name='支付宝公钥')
    c_private_key = models.TextField(verbose_name='商家私钥')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='创建时间')
    is_active = models.BooleanField(default=True, verbose_name='是否激活状态')
    last_time = models.DateTimeField(null=True, blank=True, verbose_name='最后收款时间')
    total_money = models.FloatField(default=0.0, verbose_name='总收款')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '支付宝管理'
        verbose_name_plural = verbose_name


class WXBusinessInfo(models.Model):
    name = models.CharField(max_length=50, verbose_name='收款公司名称')
    wx_mchid = models.CharField(max_length=32,verbose_name='商户号')
    wx_appid = models.CharField(max_length=32, verbose_name='微信商家appid')
    wxapi_key = models.TextField(verbose_name='微信key')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='创建时间')
    is_active = models.BooleanField(default=True, verbose_name='是否激活状态')
    last_time = models.DateTimeField(null=True, blank=True, verbose_name='最后收款时间')
    total_money = models.FloatField(default=0.0, verbose_name='总收款')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '微信管理'
        verbose_name_plural = verbose_name
