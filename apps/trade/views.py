import re, random, hashlib, time, json
from datetime import datetime
import requests
from django.shortcuts import render, redirect
# Create your views here.
from rest_framework import mixins, viewsets, views
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from utils.make_code import make_short_code
from .filters import OrdersFilter, WithDrawFilter
from user.models import UserProfile
from trade.models import OrderInfo, WithDrawMoney, BusinessInfo, WXBusinessInfo
from trade.serializers import OrderSerializer, OrderListSerializer, WithDrawSerializer, WithDrawCreateSerializer, \
    TotalNumSerializer
from utils.permissions import IsOwnerOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from decimal import Decimal
from django.http import StreamingHttpResponse, HttpResponse
# from wxpay import WXPayUtil, WXPay
from pywxpay import WXPayUtil, WXPay
from utils.pay import AliPay
from alipay_shop.settings import ALIPAY_DEBUG, APP_NOTIFY_URL, WX_NOTIFY_URL
import urllib.parse


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
        resp = {'msg': '操作成功', 'code': 200, 'data': []}
        result = WXPayUtil().xml2dict(request.body)
        print('result', result)
        verify = WXPayUtil().is_signature_valid(result, '4b2ee361b2c7b000d244ca3e60c29f62')
        pay_status = result.get("result_code", "")
        app_id = result.get('appid', '')
        c_queryset = WXBusinessInfo.objects.filter(wx_appid=app_id)
        if c_queryset:
            c_model = c_queryset[0]
            if verify and pay_status == "SUCCESS":
                print('支付成功！')
                trade_no = result.get("transaction_id", None)
                order_no = result.get("out_trade_no", None)
                print('order_no', order_no)
                total_amount = result.get("total_fee", 0)
                exited_orderqueryset = OrderInfo.objects.filter(order_no=order_no)
                if not exited_orderqueryset:
                    resp['msg'] = '订单不存在'
                    return Response('fail')
                exited_order = exited_orderqueryset[0]
                user_id = exited_order.user_id
                user_info = UserProfile.objects.filter(id=user_id)[0]
                if exited_order.pay_status == 'PAYING':
                    exited_order.trade_no = trade_no
                    exited_order.pay_status = 'TRADE_SUCCESS'
                    exited_order.pay_time = datetime.now()
                    exited_order.save()
                    # 更新用户收款
                    user_info.total_money = '%.2f' % (user_info.total_money + (int(total_amount) * 0.01))
                    user_info.save()
                    # 更新商家存钱
                    c_model.total_money = '%.2f' % (c_model.total_money + (int(total_amount) * 0.01))
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
                r = json.dumps(resp)
                headers = {'Content-Type': 'application/json'}
                try:
                    print('开始给用户post', notify_url)
                    res = requests.post(notify_url, headers=headers, data=r, timeout=5, stream=True)
                    # return Response(res.text)
                    print('res.text', res.text)
                    if res.text == 'success':
                        # headers = {'Content-Type': 'text/xml'}
                        print('res.text', res.text)
                        data = '''
                        <xml>
                          <return_code><![CDATA[SUCCESS]]></return_code>
                          <return_msg><![CDATA[OK]]></return_msg>
                        </xml>
                        '''
                        return StreamingHttpResponse(data)

                except requests.exceptions.Timeout:
                    print('给用户post异常')
                    exited_order.pay_status = 'NOTICE_FAIL'
                    exited_order.save()
                    return Response('')
        return Response('fail')

    def get(self, request):
        return HttpResponse('操作错误')


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
        m = hashlib.md5()
        m.update(new_temp.encode('utf-8'))
        my_key = m.hexdigest()
        if my_key == key:
            short_code = make_short_code(8)
            order_no = "{time_str}{userid}{randstr}".format(time_str=time.strftime("%Y%m%d%H%M%S"),
                                                            userid=user.id, randstr=short_code)
            if receive_way == 'ALIPAY':
                c_queryet = BusinessInfo.objects.filter(is_active=True).all()
                if not c_queryet:
                    resp['code'] = 404
                    resp['msg'] = '收款商户未激活'
                    return Response(resp)
                receive_c = random.choice(c_queryet)
                app_id = receive_c.c_appid
                private_key_path = receive_c.c_private_key
                ali_public_path = receive_c.alipay_public_key
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
                if str(plat_type) == '1':
                    # resp['re_url'] = 'http://127.0.0.1:8000/redirect_url/?id='+url
                    # http = urlsplit(request.build_absolute_uri(None)).scheme
                    resp['re_url'] = 'https://' + request.META['HTTP_HOST'] + '/redirect_url/?id=' + url
                    url = resp['re_url']
                else:
                    resp['re_url'] = url

                order = OrderInfo()
                order.user_id = user.id
                order.order_no = order_no
                order.pay_status = 'PAYING'
                order.total_amount = total_amount
                order.user_msg = user_msg
                order.order_id = order_id
                order.receive_way = receive_way
                order.pay_url = url
                order.plat_type = str(plat_type)
                order.save()
                resp['msg'] = '创建成功'
                resp['code'] = 200
                resp['total_amount'] = total_amount
                resp['receive_way'] = receive_way
                # resp['re_url'] = url
                return Response(resp)

            elif receive_way == 'WECHAT':
                order = OrderInfo()
                order.user_id = user.id
                order.order_no = order_no
                order.pay_status = 'PAYING'
                order.total_amount = total_amount
                order.user_msg = user_msg
                order.order_id = order_id
                order.receive_way = receive_way
                order.plat_type = str(plat_type)
                order.pay_url = 'https://' + request.META['HTTP_HOST'] + '/get_pay/?id=' + order_no
                order.save()
                resp['msg'] = '创建成功'
                resp['code'] = 200
                resp['total_amount'] = total_amount
                resp['receive_way'] = receive_way
                resp['re_url'] = 'https://' + request.META['HTTP_HOST'] + '/get_pay/?id=' + order_no + '&return_url=' + return_url
                if str(plat_type) == '0':
                    c_queryet = WXBusinessInfo.objects.filter(is_active=True).all()
                    if not c_queryet:
                        resp['code'] = 404
                        resp['msg'] = '收款商户未激活'
                        return Response(resp)
                    receive_c = random.choice(c_queryet)
                    wx_appid = receive_c.wx_appid
                    wx_mchid = receive_c.wx_mchid
                    wxapi_key = receive_c.wxapi_key
                    # 96537e694e4b1ce3e2bfb6cbd3cac3aa
                    wxpay = WXPay(app_id=wx_appid, mch_id=wx_mchid, key=wxapi_key, cert_pem_path=None,
                                  key_pem_path=None,
                                  timeout=600.0, use_sandbox=False)

                    trade_type = 'NATIVE'
                    scene_info = False

                    wxpay_resp_dict = wxpay.unifiedorder(dict(device_info='WEB', body=order_id, detail='',
                                                              out_trade_no=order_id,
                                                              total_fee=int(Decimal(total_amount) * 100),
                                                              fee_type='CNY',
                                                              notify_url=WX_NOTIFY_URL,
                                                              spbill_create_ip='27.157.112.11',
                                                              trade_type=trade_type,
                                                              scene_info=scene_info)
                                                         )

                    print('wxpay_resp_dict', wxpay_resp_dict)
                    url = wxpay_resp_dict.get('code_url', '')
                    if not url:
                        resp['code'] = 404
                        resp['msg'] = '支付渠道不正确'
                        return Response(resp)
                    resp['re_url'] = url
                return Response(resp)
                # return redirect(url)
            else:
                resp['code'] = 404
                resp['msg'] = '该渠道未开通'
                return Response(resp)
        resp['code'] = 404
        resp['msg'] = 'key匹配错误'
        return Response(resp)

    def get(self, request):
        order_id = request.GET.get('id', '')
        return_url = request.GET.get('return_url', '')
        print('order_id', order_id)
        resp = {}
        c_queryet = WXBusinessInfo.objects.filter(is_active=True).all()
        if not c_queryet:
            resp['code'] = 404
            resp['msg'] = '收款商户未激活'
            return Response(resp)
        if order_id:
            order_queryset = OrderInfo.objects.filter(order_no=order_id)
            if order_queryset:
                order_obj = order_queryset[0]
                # plat_type = order_obj.plat_type
                total_amount = order_obj.total_amount

                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
                if x_forwarded_for:
                    user_ip = x_forwarded_for.split(',')[0]  # 所以这里是真实的ip
                else:
                    user_ip = request.META.get('REMOTE_ADDR')
                # user_ip = '27.157.112.11'
                print('user_ip', user_ip)
                receive_c = random.choice(c_queryet)
                wx_appid = receive_c.wx_appid
                wx_mchid = receive_c.wx_mchid
                wxapi_key = receive_c.wxapi_key
                # 96537e694e4b1ce3e2bfb6cbd3cac3aa
                wxpay = WXPay(app_id=wx_appid, mch_id=wx_mchid, key=wxapi_key, cert_pem_path=None, key_pem_path=None,
                              timeout=600.0, use_sandbox=False)

                trade_type = 'MWEB'
                scene_info = '{"h5_info": {"type":"Wap","wap_url": "https://" + request.META["HTTP_HOST"],"wap_name": "微信支付"}}'
                wxpay_resp_dict = wxpay.unifiedorder(dict(device_info='WEB', body=order_id, detail='',
                                                          out_trade_no=order_id,
                                                          total_fee=int(Decimal(total_amount) * 100),
                                                          fee_type='CNY',
                                                          notify_url=WX_NOTIFY_URL,
                                                          spbill_create_ip=user_ip,
                                                          trade_type=trade_type,
                                                          scene_info=scene_info)
                                                     )

                print('wxpay_resp_dict', wxpay_resp_dict)
                url = wxpay_resp_dict.get('code_url', '')
                if not url:
                    url = wxpay_resp_dict.get('mweb_url', '')
                if not url:
                    resp['code'] = 404
                    resp['msg'] = '支付渠道不正确'
                    return Response(resp)
                # if str(plat_type) == '1':
                url = 'https://' + request.META['HTTP_HOST'] + '/wx_redirect/?id=' + url + '&redirect_url=' + urllib.parse.quote(return_url)
                # url = 'http://zymyun.com:8000' + '/wx_redirect/?id=' + url +'&redirect_url=' + urllib.parse.quote(return_url)
                print('url',url)
                return redirect(url, True)
        return HttpResponse('查询无效')


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
