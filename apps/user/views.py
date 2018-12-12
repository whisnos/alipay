from django.db.models import Q
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler

from user.serializers import RegisterUserSerializer
from utils.pay import AliPay
from rest_framework import viewsets, mixins, status
import json
import time
from user.models import UserProfile

User = get_user_model()


class CustomModelBackend(ModelBackend):
	def authenticate(self, request, username=None, password=None, **kwargs):
		try:
			user = User.objects.get(Q(username=username) | Q(mobile=username))
			if user.check_password(password):
				return user
		except Exception as e:
			print(e)
			return None


class RegisterUserProfileViewset(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin,
								 mixins.UpdateModelMixin):
	queryset = UserProfile.objects.all()
	serializer_class = RegisterUserSerializer

	def get_permissions(self):
		if self.action == 'retrieve':
			return [IsAuthenticated()]
		else:
			return []

	def get_object(self):
		return self.request.user

	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		user = self.perform_create(serializer)

		# 负载
		payload = jwt_payload_handler(user)
		token = jwt_encode_handler(payload)

		response_data = serializer.data
		# 加上token
		response_data["token"] = token

		headers = self.get_success_headers(response_data)

		# 返回数据
		return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

	def perform_create(self, serializer):
		# 返回的UserProfile实例对象
		return serializer.save()


def ali():
	# 沙箱环境地址：https://openhome.alipay.com/platform/appDaily.htm?tab=info
	app_id = "2016092100565912"
	# POST请求，用于最后的检测
	notify_url = "http://127.0.0.1:8000/page2/"
	# notify_url = "http://www.wupeiqi.com:8804/page2/"

	# GET请求，用于页面的跳转展示
	return_url = "http://127.0.0.1:8000/page2/"
	# return_url = "http://www.wupeiqi.com:8804/page2/"

	merchant_private_key_path = "keys/app_private_2048.txt"
	alipay_public_key_path = "keys/alipay_public_2048.txt"

	alipay = AliPay(
		appid=app_id,
		# 异步的通知接口，当在浏览器扫描创建订单后，这个时候关闭页面，此时可以在客户端或者支护宝账号里面看到这个为支付完成的信息
		app_notify_url=notify_url,
		# 同步接口，支付成功后会跳转的接口
		return_url=return_url,
		app_private_key_path=merchant_private_key_path,
		alipay_public_key_path=alipay_public_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥
		debug=True,  # 默认False,
	)
	return alipay


def index(request):
	return render(request, 'page1.html')


def page1(request):
	if request.method == "GET":
		return render(request, 'page1.html')
	else:
		money = float(request.POST.get('money'))
		alipay = ali()
		# 生成支付的url
		query_params = alipay.direct_pay(
			subject="充气式韩红",  # 商品简单描述
			out_trade_no="x2" + str(time.time()),  # 商户订单号
			total_amount=money,  # 交易金额(单位: 元 保留俩位小数)
		)

		pay_url = "https://openapi.alipaydev.com/gateway.do?{0}".format(query_params)
		print('支付宝支付链接：', pay_url)
		return redirect(pay_url)


def page2(request):
	alipay = ali()
	print('99999999999999999999')
	if request.method == "POST":
		# 检测是否支付成功
		# 去请求体中获取所有返回的数据：状态/订单号
		from urllib.parse import parse_qs
		body_str = request.body.decode('utf-8')
		post_data = parse_qs(body_str)

		post_dict = {}
		for k, v in post_data.items():
			post_dict[k] = v[0]
		print(post_dict)

		sign = post_dict.pop('sign', None)
		status = alipay.verify(post_dict, sign)
		print('POST验证', status)
		return HttpResponse('POST返回')

	else:
		params = request.GET.dict()
		print(type(params), params)
		sign = params.pop('sign', None)
		status = alipay.verify(params, sign)
		print('GET验证', status)
		return HttpResponse('支付成功')
