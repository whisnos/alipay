from django.db.models import Q
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from rest_framework.authentication import SessionAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler

from trade.models import OrderInfo
from trade.serializers import OrderListSerializer
from user.serializers import RegisterUserSerializer, UserUpdateSerializer, UserDetailSerializer, NoticeInfoSerializer
from utils.pay import AliPay
from rest_framework import viewsets, mixins, status, views
import time
from user.models import UserProfile, NoticeInfo
from utils.permissions import IsOwnerOrReadOnly

User = get_user_model()

class CustomModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username) | Q(mobile=username))
            if user.check_password(password):
                return user
        except Exception as e:
            # print(e)
            return None


class RegisterUserProfileViewset(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                                 mixins.UpdateModelMixin):
    '''
    total_money：当前收款余额
    total_count_num：总订单数 - 包括未支付
    total_count_success_num：总成功收款数
    today_receive：今日收款金额
    today_count_num：今日订单数 - 包括未支付
    today_count_success_num：今日订单数 仅限 支付成功
    today_withdraw_success_money：今日提现到账金额
    total_withdraw_success_money：总提现到账金额
    '''
    serializer_class = RegisterUserSerializer
    queryset = UserProfile.objects.all()
    # JWT认证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return UserDetailSerializer
        elif self.action == "create":
            return RegisterUserSerializer

        return UserDetailSerializer

    def get_permissions(self):
        if self.action == 'retrieve':
            return [IsAuthenticated()]
        elif self.action == "create":
            return []
        else:
            return []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.perform_create(serializer)

        # 负载
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        response_data = serializer.data
        # 加上token
        # response_data["token"] = token

        # response_data["username"] = user.username
        headers = self.get_success_headers(response_data)

        # 返回数据
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

    def get_object(self):
        return self.request.user

    def perform_create(self, serializer):
        # 返回的UserProfile实例对象
        return serializer.save()

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = self.request.data.get('password', '')
        password2 = self.request.data.get('password2', '')
        notify_url = self.request.data.get('notify_url', '')
        # print(456, notify_url)
        qq = self.request.data.get('qq', '')
        # print(11, password, password2)
        user = self.get_object()
        # print(88, qq)
        if password == password2:
            if password:
                user.set_password(password)
        if notify_url:
            user.notify_url = notify_url
        if qq:
            user.qq = qq
        user.save()
        # response_data = serializer.data
        # headers = self.get_success_headers(response_data)
        return Response(status=status.HTTP_201_CREATED)


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


class NoticeListPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'page'


class NoticeInfoViewset(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    serializer_class = NoticeInfoSerializer
    queryset = NoticeInfo.objects.all().order_by('-add_time')
    # JWT认证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    pagination_class = NoticeListPagination

    def get_permissions(self):
        if self.action == 'retrieve':
            return [IsAuthenticated()]
        elif self.action == "create":
            return []
        else:
            return []


class ChartInfoViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    # pagination_class = NoticeListPagination
    serializer_class = OrderListSerializer
    # today_time = time.strftime('%Y-%m-%d', time.localtime())
    # queryset = OrderInfo.objects.filter(add_time__gte=today_time,pay_status__icontains='TRADE_SUCCESS').order_by('-add_time')
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def get_permissions(self):
        if self.action == 'retrieve':
            return [IsAuthenticated()]
        elif self.action == "create":
            return []
        else:
            return []

    def get_queryset(self):
        user = self.request.user
        if user:
            today_time = time.strftime('%Y-%m-%d', time.localtime())
            return OrderInfo.objects.filter(user=self.request.user, add_time__gte=today_time,
                                       pay_status__icontains='TRADE_SUCCESS').order_by('-add_time')
        return []


class QueryOrderView(views.APIView):
    def post(self, request):
        processed_dict = {}
        resp = {'msg': '订单不存在', 'code': 400}
        for key, value in request.data.items():
            processed_dict[key] = value
        uid = processed_dict.get('uid', '')
        # auth_code = processed_dict.get('auth_code', '')
        order_no = processed_dict.get('order_no', '')
        user_queryset = UserProfile.objects.filter(uid=uid)
        if user_queryset:
            user = user_queryset[0]
            order_queryset = OrderInfo.objects.filter(user=user, order_no=order_no)
            if order_queryset:
                order = order_queryset[0]
                resp['msg'] = '查询成功'
                resp['code'] = 200
                resp['money'] = order.total_amount
                resp['usr_msg'] = order.user_msg
                resp['add_time'] = order.add_time
                resp['pay_status'] = order.pay_status
                resp['order_no'] = order.order_no
                resp['order_id'] = order.order_id
                resp['receive_way'] = order.receive_way
                resp['pay_time'] = order.pay_time
                return Response(resp)
        return Response(resp)
