import hashlib
from time import strftime, localtime
# print(strftime('%Y-%m-%d',localtime()))
a='7ec5e9780e7c11e9bb97d8cb8a770be3ZUuo3QxlbwyjDTWem9aSNGBaZGfGxFes200ALIPAYhttp://www.baidu.com/1113111111'
# print('%.2f' % a)
m = hashlib.md5()
m.update(a.encode("utf-8"))
sign=m.hexdigest()
print(sign)
b='银行:招商银行\n'
c='开户行:福建省漳州市\n'
d='姓名:小王\n'
e='银行账号:12212@qq.com'

# print(b+c+d+e)

# str1 ="第一行##第二行##第三行"
# str1.split()
# print(str1)
# print(str2)