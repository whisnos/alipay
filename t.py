import hashlib
import re
from time import strftime, localtime

# print(strftime('%Y-%m-%d',localtime()))
a = '45957614119411e99c2800163e0472b2HB9KW8H96Q5CcmZcMvklmPmxlcAQJpUk0.01WECHAThttp://zymyun.com1113111111'
# print('%.2f' % a)
m = hashlib.md5()
m.update(a.encode("utf-8"))
sign = m.hexdigest()
print(sign)

user_money = 5.53
cun_money = '%.2f' % (user_money + float(2.1))
# print(cun_money)

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

total_amount = '1099'
# print((int(total_amount)*0.01))
# print('ype(total_amount)', type(total_amount))
# if (type(total_amount) == str):
#     num = int(int(total_amount) * 100)
# else:
#     num = int((total_amount) * 100)
# print(num)
new_data_dict=wxpay.fill_request_data(dict(device_info='WEB',
                                          body='测试商家-商品类目',
                                          detail='',
                                          out_trade_no='2016090910595900000022',
                                          total_fee=1,
                                          fee_type='CNY',
                                          notify_url='http://120.34.182.49:8000/wxpay/receive/',
                                          spbill_create_ip='123.12.12.123',
                                          trade_type='NATIVE'))


