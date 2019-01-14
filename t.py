import hashlib
import re
from time import strftime, localtime

# print(strftime('%Y-%m-%d',localtime()))
a = '7cf0531c10d711e98efed8cb8a770be3V9aBrYxo9AeSyBJmsH6NkG28ZzaRmFNp0.02WECHAThttp://127.0.0.1:8000/page2/1113111111'
# print('%.2f' % a)
m = hashlib.md5()
m.update(a.encode("utf-8"))
sign = m.hexdigest()
print(sign)

user_money = 5.53
cun_money = '%.2f' % (user_money + float(2.1))
# print(cun_money)

from pywxpay import WXPay

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
total_amount = '0.01'
# print(round(float(total_amount)))
# print('ype(total_amount)', type(total_amount))
# if (type(total_amount) == str):
#     num = int(int(total_amount) * 100)
# else:
#     num = int((total_amount) * 100)
# print(num)
