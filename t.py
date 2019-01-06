import hashlib
import re
from time import strftime, localtime
# print(strftime('%Y-%m-%d',localtime()))
a='7cf0531c10d711e98efed8cb8a770be3V9aBrYxo9AeSyBJmsH6NkG28ZzaRmFNp200ALIPAYhttp://127.0.0.1:8000/page2/1113111111'
# print('%.2f' % a)
m = hashlib.md5()
m.update(a.encode("utf-8"))
sign=m.hexdigest()
# print(sign)
total_amount=0.03
patt = re.test(r'(^[1-9]([0-9]{1,4})?(\.[0-9]{1,2})?$)|(^(0){1}$)|(^[0-9]\.[0-9]([0-9])?$)', total_amount)
# print(patt)
a='测试1435'