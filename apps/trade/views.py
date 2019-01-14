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
from trade.serializers import OrderSerializer, OrderListSerializer, \
    GetPaySerializer, WithDrawSerializer, WithDrawCreateSerializer, TotalNumSerializer
from utils.pay import AliPay
from utils.permissions import IsOwnerOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from alipay_shop.settings import ALIPAY_DEBUG


class OrderListPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 100


class OrderViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
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

    def get_serializer_class(self):
        return OrderListSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return OrderInfo.objects.all().order_by('id')
        user = self.request.user
        if user:
            return OrderInfo.objects.filter(user=self.request.user).order_by('-add_time')
        return []


class AlipayReceiveView(views.APIView):
    def post(self, request):
        resp = {'msg': '操作成功', 'code': 200, 'data': []}
        processed_dict = {}
        for key, value in request.data.items():
            processed_dict[key] = value
        sign = processed_dict.pop("sign", None)
        app_id = processed_dict.get('app_id', '')
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
                debug=ALIPAY_DEBUG,  # 默认False,
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
            print('pay_status', pay_status)
            if verify_result is True and pay_status == "TRADE_SUCCESS":
                trade_no = processed_dict.get("trade_no", None)
                order_no = processed_dict.get("out_trade_no", None)
                total_amount = processed_dict.get("total_amount", 0)
                exited_order = OrderInfo.objects.filter(order_no=order_no)[0]
                user_id = exited_order.user_id
                user_info = UserProfile.objects.filter(id=user_id)[0]
                if exited_order.pay_status == 'PAYING':
                    exited_order.trade_no = trade_no
                    exited_order.pay_status = pay_status
                    exited_order.pay_time = datetime.now()
                    exited_order.save()
                    # 更新用户收款
                    user_info.total_money = '%.2f' % (user_info.total_money + float(total_amount))
                    user_info.save()
                    # 更新商家存钱
                    c_model.total_money = '%.2f' % (c_model.total_money + float(total_amount))
                    c_model.last_time = datetime.now()
                    c_model.save()

                '支付状态，下单时间，支付时间，商户订单号'
                notify_url = user_info.notify_url
                if not notify_url:
                    return Response('success')
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
                    res = requests.post(notify_url, headers=headers, data=r, timeout=5, stream=True)
                    return Response(res.text)
                except requests.exceptions.Timeout:
                    exited_order.pay_status = 'NOTICE_FAIL'
                    exited_order.save()
                    return Response('')
        resp = {'msg': '验签失败', 'code': 400, 'data': {}}
        return Response(resp)

    def get(self, request):
        return Response('操作错误')


class WxpayReceiveView(views.APIView):
    def post(self, request):
        print('11111111')
        # processed_dict = {}
        # for key, value in request.data.items():
        #     processed_dict[key] = value
        # resp = {'msg': '验签失败', 'code': 400, 'data': {}}

        from pywxpay import WXPayUtil
        wxpayutil = WXPayUtil()
        print('request.body', request.body)
        result = wxpayutil.xml2dict(request.body)
        print('result', result)

        verify = wxpayutil.is_signature_valid(result, '4b2ee361b2c7b000d244ca3e60c29f62')
        if verify:
            pass
        print('verify', verify)
        return Response('success')

    def get(self, request):
        return Response('操作错误')


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
            c_queryet = BusinessInfo.objects.filter(is_active=True).all()
            if not c_queryet:
                resp['code'] = 404
                resp['msg'] = '收款商户未激活'
                return Response(resp)

            import time
            from utils.make_code import make_short_code
            short_code = make_short_code(8)
            order_no = "{time_str}{userid}{randstr}".format(time_str=time.strftime("%Y%m%d%H%M%S"),
                                                            userid=user.id, randstr=short_code)
            if receive_way == 'ALIPAY':
                receive_c = random.choice(c_queryet)
                app_id = receive_c.c_appid
                private_key_path = receive_c.c_private_key
                ali_public_path = receive_c.alipay_public_key
                from utils.pay import AliPay
                from alipay_shop.settings import APP_NOTIFY_URL
                alipay = AliPay(
                    appid=app_id,
                    app_notify_url=APP_NOTIFY_URL,
                    app_private_key_path=private_key_path,  # 个人私钥
                    alipay_public_key_path=ali_public_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
                    debug=ALIPAY_DEBUG,  # 默认False,
                    return_url=return_url,
                    plat_type=str(plat_type),
                )
                url = alipay.direct_pay(
                    subject=order_no,
                    out_trade_no=order_no,
                    total_amount=total_amount
                )
                order = OrderInfo()
                order.user_id = user.id
                order.order_no = order_no
                order.pay_status = 'PAYING'
                order.total_amount = total_amount
                order.user_msg = user_msg
                order.order_id = order_id
                order.receive_way = receive_way
                order.pay_url = url
                order.save()
                resp['msg'] = '创建成功'
                resp['code'] = 200
                resp['total_amount'] = total_amount
                resp['receive_way'] = receive_way
                if str(plat_type) == '1':
                    # resp['re_url'] = 'http://127.0.0.1:8000/redirect_url/?id='+url
                    # http = urlsplit(request.build_absolute_uri(None)).scheme
                    resp['re_url'] = 'https://' + request.META['HTTP_HOST'] + '/redirect_url/?id=' + url
                else:
                    resp['re_url'] = url
                return Response(resp)

            elif receive_way == 'WECHAT':
                from pywxpay import WXPay
                wxpay = WXPay(app_id='wx1b0782ff589aa9a6',
                              mch_id='1489970272',
                              key='4b2ee361b2c7b000d244ca3e60c29f62',
                              cert_pem_path=None,
                              key_pem_path=None,
                              timeout=600.0)
                from decimal import Decimal
                print('total_amount',total_amount)
                d = Decimal(total_amount)
                print('d',d)
                wxpay_resp_dict = wxpay.unifiedorder(dict(device_info='WEB',
                                                          body=order_no,
                                                          detail='',
                                                          out_trade_no=order_no,
                                                          total_fee=int(d*100),
                                                          fee_type='CNY',
                                                          notify_url='http://120.34.182.49:8000/wxpay/receive/',
                                                          spbill_create_ip='123.12.12.123',
                                                          trade_type='NATIVE')
                                                     )
                print('wxpay_resp_dict',wxpay_resp_dict)
                url=wxpay_resp_dict.get('code_url','')
                order = OrderInfo()
                order.user_id = user.id
                order.order_no = order_no
                order.pay_status = 'PAYING'
                order.total_amount = total_amount
                order.user_msg = user_msg
                order.order_id = order_id
                order.receive_way = receive_way
                order.pay_url = url
                order.save()
                resp['msg'] = '创建成功'
                resp['code'] = 200
                resp['total_amount'] = total_amount
                resp['receive_way'] = receive_way
                resp['re_url'] = url
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
            return WithDrawMoney.objects.all().order_by('-add_time')
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
