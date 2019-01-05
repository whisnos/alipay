'''
UserProfile 用户表
OrderInfo 订单表



'''

# user models设计
'''
UserProfile 用户表 字段有如下：
用户名：name
性别：gender
邮箱：email
手机：mobile
#替换系统的用户
AUTH_USER_MODEL = "users.UserProfile"



'''
from django.db import models
from django.contrib.auth.models import AbstractUser

'''
创建trade应用
订单OrderInfo设计
'''


class OrderInfo(models.Model):
    ORDER_STATUS = (
        ("PAYING", "待支付"),
        ("TRADE_SUCESS", "支付成功"),
        ("TRADE_CLOSE", "支付关闭"),
        ("TRADE_FAIL", "支付失败"),
        ("TRADE_FINSHED", "交易结束"),
    )
    user = models.ForeignKey(User, verbose_name=u"用户")
    order_sn = models.CharField(max_length=30, unique=True, verbose_name="订单号")
    trade_no = models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name="订单号")
    pay_status = models.CharField(default="PAYING", max_length=30, choices=ORDER_STATUS, verbose_name="订单状态")
    post_script = models.CharField(max_length=200, verbose_name="订单留言")
    order_mount = models.FloatField(default=0.0, verbose_name="订单金额")
    pay_time = models.DateTimeField(null=True, blank=True, verbose_name="支付时间")
    signer_mobile = models.CharField(max_length=11, verbose_name="联系电话")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "订单"
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.order_sn)


'''
user_operation应用
用户收藏UserFav的设计
用户留言UserLeavingMessage的设计
'''
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFav(models.Model):
    user = models.ForeignKey(User, verbose_name="用户")
    goods = models.ForeignKey(Goods, verbose_name="商品")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "用户收藏"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s收藏了:%s" % (self.user.name, self.goods.goods_sn)


class UserLeavingMessage(models.Model):
    """
    用户留言
    """

    MSG_TYPE = (
        (1, "留言"),
        (2, "投诉"),
        (3, "询问"),
        (4, "售后"),
        (5, "求购"),

    )
    user = models.ForeignKey(User, verbose_name="用户")
    subject = models.CharField(max_length=100, default="", verbose_name="留言主题")
    msg_type = models.IntegerField(default=1, choices=MSG_TYPE, verbose_name="留言类型",
                                   help_text="留言类型: 1(留言),2(投诉),3(询问),4(售后),5(求购)")
    message = models.CharField(max_length=500, verbose_name="留言内容")
    file = models.FileField(upload_to="message/images/", verbose_name="上传的文件", help_text="上传的文件")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "用户留言"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s留言:%s" % (self.user.name, self.subject)


'''
class VerifyCodeAdmin(object):
	    list_display = ['code', 'mobile', "add_time"]
	    xadmin.site.register(VerifyCode, VerifyCodeAdmin)
	    
class GlobalSettings(object):
		site_title = "XXX后台"
			site_footer = "shop"	    
			
xadmin.site.register(views.CommAdminView,GlobalSettings)	        
'''
'''
安装完软件
cnpm的下载和安装

npm install cnpm -g --registry=https://registry.npm.taobao.org
出错 
清除缓存命令：npm cache clean --force

然后 进vue项目 目录下
执行：cnpm install 命令
该命令，是安装依赖的包


运行项目命令：cnpm run dev

访问前端项目
http://localhost:8080
'''
