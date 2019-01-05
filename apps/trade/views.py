import re, random
from datetime import datetime
import requests

# Create your views here.
from rest_framework import mixins, viewsets, serializers, views, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .filters import OrdersFilter, WithDrawFilter
from user.models import UserProfile
from trade.models import OrderInfo, WithDrawMoney, BusinessInfo
from trade.serializers import OrderDetailSerializer, OrderSerializer, OrderListSerializer, \
    GetPaySerializer, WithDrawSerializer, WithDrawCreateSerializer, TotalNumSerializer
from utils.pay import AliPay
from utils.permissions import IsOwnerOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination


class OrderListPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 100


class OrderViewset(mixins.DestroyModelMixin, mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    """
    订单管理:
        list:  获取个人订单
        create: 添加订单
        delete: 删除订单
        retrieve: 订单详情信息
    """
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = OrderSerializer
    pagination_class = OrderListPagination
    '状态,时间范围，金额范围'
    filter_backends = (DjangoFilterBackend,)
    filter_class = OrdersFilter

    # 搜索字段
    # ordering_fields = ('add_time',)
    def get_serializer_class(self):
        if self.action == "retrieve":
            return OrderDetailSerializer
        if self.action == "list":
            return OrderListSerializer
        else:
            return OrderSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            # print('当前用户是管理员', self.request.user)
            return OrderInfo.objects.all().order_by('id')
        # print(11111111111111111111, self.request.user)
        user = self.request.user
        if user:
            return OrderInfo.objects.filter(user=self.request.user).order_by('-add_time')
        return []


class AlipayReceiveView(views.APIView):
    def post(self, request):
        # print('支付宝开始进入post')
        resp = {'msg': '操作成功', 'code': 200, 'data': []}
        processed_dict = {}
        for key, value in request.data.items():
            processed_dict[key] = value
        sign = processed_dict.pop("sign", None)
        app_id = processed_dict.get('app_id', '')
        # print('看看看看看看2支付后，post回来 商家app_id', app_id)
        c_queryset = BusinessInfo.objects.filter(c_appid=app_id)
        if c_queryset:
            c_model = c_queryset[0]
            private_key_path = c_model.c_private_key
            ali_public_path = c_model.alipay_public_key
            alipay = AliPay(
                appid=app_id,
                app_notify_url=None,
                app_private_key_path=private_key_path,
                alipay_public_key_path=ali_public_path,
                debug=True,  # 默认False,
                return_url=None
            )
            try:
                # 验证通过返回True
                verify_result = alipay.verify(processed_dict, sign)
            except:
                resp['msg'] = '操作失败'
                resp['code'] = 400
                return Response(resp)
            pay_status = processed_dict.get("trade_status", "")

            if verify_result is True and pay_status == "TRADE_SUCCESS":
                trade_no = processed_dict.get("trade_no", None)
                order_no = processed_dict.get("out_trade_no", None)
                # pay_status = processed_dict.get("trade_status", "")
                total_amount = processed_dict.get("total_amount", 0)
                # print('金额', total_amount)
                # print('支付成功回调跳转后的打印', order_no, '支付宝交易号：', trade_no)
                exited_order = OrderInfo.objects.filter(order_no=order_no)[0]
                user_id = exited_order.user_id
                user_info = UserProfile.objects.filter(id=user_id)[0]
                if exited_order.pay_status == 'PAYING':
                    # for exited_order in exited_orders:
                    exited_order.trade_no = trade_no
                    exited_order.pay_status = pay_status
                    exited_order.pay_time = datetime.now()
                    exited_order.save()
                    # 更新用户收款
                    # from alipay_shop.settings import SERVICE_FEE
                    user_info.total_money += float(total_amount)
                    user_info.save()
                    # 更新商家存钱
                    # print('商家：----------------------', c_model.name, '成功收款:', total_amount)
                    c_model.total_money += float(total_amount)
                    c_model.last_time = datetime.now()
                    c_model.save()

                '支付状态，下单时间，支付时间，商户订单号'
                notify_url = user_info.notify_url
                # print('当前用户的回调接收地址：', notify_url)
                if not notify_url:
                    # resp['msg']='notify_url参数为空'
                    return Response('success')
                # print('notify_url', notify_url)
                data_dict = {}
                data_dict['pay_status'] = pay_status
                data_dict['add_time'] = str(exited_order.add_time)
                data_dict['pay_time'] = str(exited_order.pay_time)
                data_dict['total_amount'] = total_amount
                data_dict['order_id'] = exited_order.order_id
                data_dict['order_no'] = exited_order.order_no
                data_dict['user_msg'] = exited_order.user_msg
                resp['data'] = data_dict
                import json
                r = json.dumps(resp)
                headers = {'Content-Type': 'application/json'}
                try:
                    res = requests.post(notify_url, headers=headers, data=r, timeout=5)
                    if res.status_code == 200:
                        # print('200', res.text)
                        return Response(res.text)
                    else:
                        # print('订单支付成功了，但通知失败')
                        exited_order.pay_status = 'NOTICE_FAIL'
                        exited_order.save()
                except requests.exceptions.Timeout:
                    # print('订单支付成功了，post异常，但通知失败')
                    exited_order.pay_status = 'NOTICE_FAIL'
                    exited_order.save()
                    return Response('')
                # res = requests.post(notify_url,headers=headers,data=r,timeout=15)
                # print('res.txt',res.content)
                # print('头部',res.headers)
        resp = {'msg': '验签失败', 'code': 400, 'data': {}}
        return Response(resp)

    def get(self, request):
        # print(request.data)
        return Response('22222222')


class GetPayView(views.APIView):
    def post(self, request):
        processed_dict = {}
        resp = {'msg': '操作成功'}
        for key, value in request.data.items():
            processed_dict[key] = value
        uid = processed_dict.get('uid', '')
        total_amount = processed_dict.get('total_amount', '')
        user_msg = processed_dict.get('user_msg', '')
        order_id = processed_dict.get('order_id', '')
        receive_way = processed_dict.get('receive_way', 'ALIPAY')
        key = processed_dict.get('key', '')
        return_url = processed_dict.get('return_url', '')
        plat_type = processed_dict.get('plat_type', '0')  # 0 pc
        user_queryset = UserProfile.objects.filter(uid=uid)
        if not user_queryset:
            resp['msg'] = 'uid或者auth_code错误，请重试~~'
            return Response(resp, status=404)
        patt = re.match(r'(^[1-9]([0-9]{1,4})?(\.[0-9]{1,2})?$)|(^(0){1}$)|(^[0-9]\.[0-9]([0-9])?$)', total_amount)
        try:
            patt.group()
        except:
            resp['msg'] = '金额输入错误，请重试~~0.01到5万间'
            return Response(resp, status=404)
        if not order_id:
            resp['msg'] = '请填写订单号~~'
            return Response(resp, status=404)
        if not return_url:
            resp['msg'] = '请填写正确跳转url~~'
            return Response(resp, status=404)
        user = user_queryset[0]
        # 加密 uid+auth_code+total_amount+receive_way+return_url+order_id
        auth_code = user.auth_code
        new_temp = str(uid + auth_code + total_amount + receive_way + return_url + order_id)
        import hashlib
        m = hashlib.md5()
        m.update(new_temp.encode('utf-8'))
        my_key = m.hexdigest()
        if my_key == key:
            # print('get_pay后获取用户信息 用户手机号:', user.mobile)
            c_queryet = BusinessInfo.objects.filter(is_active=True).all()
            if not c_queryet:
                resp['code'] = 404
                resp['msg'] = '收款商户未激活'
                return Response(resp)
            receive_c = random.choice(c_queryet)
            app_id = receive_c.c_appid
            # print('随机获取商家收款app_id：', app_id)
            private_key_path = receive_c.c_private_key
            ali_public_path = receive_c.alipay_public_key
            from utils.pay import AliPay
            from alipay_shop.settings import APP_NOTIFY_URL
            alipay = AliPay(
                appid=app_id,
                app_notify_url=APP_NOTIFY_URL,
                app_private_key_path=private_key_path,  # 个人私钥
                alipay_public_key_path=ali_public_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
                debug=True,  # 默认False,
                # return_url="http://120.43.159.62:8000/alipay/return/"
                return_url=return_url,
                plat_type=str(plat_type),
            )
            import time
            from utils.make_code import make_short_code
            short_code = make_short_code(8)
            order_no = "{time_str}{userid}{randstr}".format(time_str=time.strftime("%Y%m%d%H%M%S"),
                                                            userid=user.id, randstr=short_code)
            url = alipay.direct_pay(
                subject=order_no,
                out_trade_no=order_no,
                total_amount=total_amount
            )
            # 沙箱环境
            re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)
            # print('生成的支付链接', re_url)
            order = OrderInfo()
            order.user_id = user.id
            order.order_no = order_no
            order.pay_status = 'PAYING'
            order.total_amount = total_amount
            order.user_msg = user_msg
            order.order_id = order_id
            order.receive_way = receive_way
            order.pay_url = re_url
            # order.time_rate = user.service_rate
            order.save()
            resp['msg'] = '创建成功'
            resp['code'] = 200
            resp['total_amount'] = total_amount
            resp['receive_way'] = receive_way
            resp['re_url'] = re_url
            return Response(resp)
        resp['code'] = 404
        resp['msg'] = 'key匹配错误'
        return Response(resp)


class WithDrawViewset(mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                      mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = WithDrawSerializer
    pagination_class = OrderListPagination
    filter_backends = (DjangoFilterBackend,)
    filter_class = WithDrawFilter

    def get_serializer_class(self):
        if self.action == "retrieve":
            return WithDrawSerializer
        elif self.action == "create":
            return WithDrawCreateSerializer
        else:
            return WithDrawSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            # print('当前用户是管理员', self.request.user)
            return WithDrawMoney.objects.all().order_by('-add_time')
        # print(11111111111111111111, self.request.user)
        user = self.request.user
        if user:
            return WithDrawMoney.objects.filter(user=self.request.user).order_by('-add_time')
        return []


class TotalNumViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = TotalNumSerializer

    def get_queryset(self):
        return (OrderInfo.objects.filter(user=self.request.user)[0:1])
