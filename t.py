import hashlib
import re
from time import strftime, localtime
# print(strftime('%Y-%m-%d',localtime()))
a='45957614119411e99c2800163e0472b2HB9KW8H96Q5CcmZcMvklmPmxlcAQJpUk0.01ALIPAYhttp://third.show.com/third/airui/return.php123456'
# print('%.2f' % a)
m = hashlib.md5()
m.update(a.encode("utf-8"))
sign=m.hexdigest()
# print(sign)

user_money=5.53
cun_money='%.2f'%(user_money+float(2.1))
# print(cun_money)