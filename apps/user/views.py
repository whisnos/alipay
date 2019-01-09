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

        response_data = serializer.data
        headers = self.get_success_headers(response_data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

    def get_object(self):
        return self.request.user

    def perform_create(self, serializer):
        return serializer.save()

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = self.request.data.get('password', '')
        password2 = self.request.data.get('password2', '')
        notify_url = self.request.data.get('notify_url', '')
        qq = self.request.data.get('qq', '')
        user = self.get_object()
        if password == password2:
            if password:
                user.set_password(password)
        if notify_url:
            user.notify_url = notify_url
        if qq:
            user.qq = qq
        user.save()
        return Response(status=status.HTTP_201_CREATED)


class NoticeListPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'page'


class NoticeInfoViewset(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    serializer_class = NoticeInfoSerializer
    queryset = NoticeInfo.objects.all().order_by('-add_time')
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


from django.db.models import Q


class ChartInfoViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = OrderListSerializer
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
            return OrderInfo.objects.filter(
                Q(pay_status__icontains='TRADE_SUCCESS') | Q(pay_status__icontains='NOTICE_FAIL'),
                user=self.request.user, add_time__gte=today_time,
            ).order_by('-add_time')
        return []


class QueryOrderView(views.APIView):
    def post(self, request):
        processed_dict = {}
        resp = {'msg': '订单不存在', 'code': 400}
        for key, value in request.data.items():
            processed_dict[key] = value
        uid = processed_dict.get('uid', '')
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


def redirect_url(request):
    # if request.method == 'POST':
    pay_url = request.get_full_path()
    url_list = pay_url.split('/redirect_url/?id=')
    if len(url_list) == 2:
        pay_url = url_list[1]
        if pay_url:
            return render(request, 'redi.html', {
                "pay_url": (pay_url)
            })
        else:
            return HttpResponse('链接错误')
    else:
        return HttpResponse('链接错误')
