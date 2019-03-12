import datetime
import hashlib
import json
import re
import time
from time import strftime, localtime

id = '1'
userid_list = ['1']
if id in userid_list:
    print(1)
# import requests
# notify_url='https://www.baiddfau.com/'
# headers = {'Content-Type': 'application/json'}
# data_dict={}
# resp={}
# data_dict['order_no'] = '123'
# data_dict['user_msg'] = '456'
# resp['data'] = data_dict
# r = json.dumps(resp)
# res = requests.post(notify_url, headers=headers, data=r, timeout=10, stream=True)
# print(res.text)
# print(strftime('%Y-%m-%d',localtime()))
a = '7cf0531c10d711e98efed8cb8a770be3V9aBrYxo9AeSyBJmsH6NkG28ZzaRmFNp0.01WECHAThttp://zymyun.com/1113111111'
a = '45957614119411e99c2800163e0472b2HB9KW8H96Q5CcmZcMvklmPmxlcAQJpUk0.01WECHAThttp://www.baidu.com/1113111111'
a = '733ca02631d411e9b6fed8cb8a770be3Yz7aUAPCxXS39BzEHyUiwSlLK8k3VdQY101http://www.baidu.com/201902231113111111'
a = "101" + "95555" + "VehkwKBOx1rD979GLOKygXfPZnuy7p3Z"
a = 'e10adc3949ba59abbe56e057f20f883e'
# print('%.2f' % a)
m = hashlib.md5()
m.update(a.encode("utf-8"))
sign = m.hexdigest()
# print(sign)

b = '-0.05'
# if re.match(r'(^[1-4]([0-9]{1,4})?(\.[0-9]{1,2})?$)|(^[0-9]\.[0-9]([0-9])?$)|(^[1-5]([0-9]{1,3})?(\.[0-9]{1,2})?$)', str(b)):
#     print('正确')
# else:
#     print('错误')
import random
# print(random.uniform(-1,1))
# print(time.time()) # 1548406890.77133
# print(time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time())))
# user_money = 5.53
# cun_money = '%.2f' % (user_money + float(2.1))
# print(cun_money)
# import base64
# pay_url={'age': 10, 'name': 'yct'}
# pay_url = base64.b64encode(pay_url)
# print('pay_url',pay_url)
from pywxpay import WXPay, WXPayUtil

wxpay = WXPay(app_id='wx1b0782ff589aa9a6',
              mch_id='1489970272',
              key='4b2ee361b2c7b000d244ca3e60c29f62',
              cert_pem_path='./keys/apiclient_cert.pem',
              key_pem_path='./keys/apiclient_key.pem',
              timeout=600.0)

wxpay_resp_dict = wxpay.unifiedorder(dict(device_info='WEB',
                                          body='测试商家-商品类目',
                                          detail='',
                                          out_trade_no='2016090910595900000022',
                                          total_fee=1,
                                          fee_type='CNY',
                                          notify_url='http://120.34.182.49:8000/wxpay/receive/',
                                          spbill_create_ip='123.12.12.123',
                                          trade_type='NATIVE')
                                     )

# print(wxpay_resp_dict)
from decimal import Decimal

# print(patt)
total_amount = '1099'
# print((int(total_amount)*0.01))
# print('ype(total_amount)', type(total_amount))
# if (type(total_amount) == str):
#     num = int(int(total_amount) * 100)
# else:
#     num = int((total_amount) * 100)
# print(num)
add_hour = datetime.datetime.now() - datetime.timedelta(days=1)
add_hour = (datetime.datetime.now()).strftime('%Y%m%d%H%M%S')
# print(datetime.datetime.now())
month_time = datetime.datetime(datetime.date.today().year, datetime.date.today().month, 1)
# future_mouth_first = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month + 1, 23, 59, 59)
# print(month_time)

new_data_dict = wxpay.fill_request_data(dict(device_info='WEB',
                                             body='测试商家-商品类目',
                                             detail='',
                                             out_trade_no='2016090910595900000022',
                                             total_fee=1,
                                             fee_type='CNY',
                                             notify_url='http://120.34.182.49:8000/wxpay/receive/',
                                             spbill_create_ip='123.12.12.123',
                                             trade_type='NATIVE'))

obj = 'B'
# if not re.match(r'^0\.(0[1-9]|[1-9]{1,2})$', obj):
#    print('格式错误')
# print(1)
if '0':
    print(2)

L1 = [1, 2, 3, 4, 5, 6]
L2 = [1, 2, 3, 4, 5, 6]
A = [1, 5]
B = [3, 5, 6]

for a in L1:
    for b in L2:
        if a == b:
            print(1)
