import hashlib
import re
from time import strftime, localtime

# print(strftime('%Y-%m-%d',localtime()))
a = '45957614119411e99c2800163e0472b2HB9KW8H96Q5CcmZcMvklmPmxlcAQJpUk0.01ALIPAYhttp://third.show.com/third/airui/return.php123456'
# print('%.2f' % a)
m = hashlib.md5()
m.update(a.encode("utf-8"))
sign = m.hexdigest()
# print(sign)

user_money = 5.53
cun_money = '%.2f' % (user_money + float(2.1))
# print(cun_money)

from pywxpay import WXPay
wxpay = WXPay(app_id='wx8888888998',
              mch_id='8888888',
              key='123434556677888999987766543543322',
              cert_pem_path='./keys/apiclient_cert.pem',
              key_pem_path='./keys/apiclient_key.pem',
              timeout=600.0)

wxpay_resp_dict = wxpay.unifiedorder(dict(device_info='WEB',
                                          body='测试商家-商品类目',
                                          detail='',
                                          out_trade_no='2016090910595900000012',
                                          total_fee=1,
                                          fee_type='CNY',
                                          notify_url='http://www.example.com/wxpay/notify',
                                          spbill_create_ip='123.12.12.123',
                                          trade_type='NATIVE')
                                     )

print(wxpay_resp_dict)
