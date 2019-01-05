from .models import OrderInfo, WithDrawMoney, BusinessInfo
import xadmin


class OrderInfoAdmin(object):
    # 展示字段
    list_display = ['order_no', 'user', 'pay_status', 'total_amount', 'trade_no', 'pay_time', 'user_msg']

    # 搜索
    # search_fields = ['order_no', 'order_id', 'user_msg']

    # 过滤
    list_filter = ['pay_status', 'order_id', 'order_no', 'user', 'add_time']

    # 小图标
    model_icon = 'fa fa-th-list'

    # 只读字段
    readonly_fields = ['user','pay_time', 'add_time', 'total_amount', 'order_no', 'trade_no',
                       'receive_way', 'order_id', 'pay_url']
    # 每页显示几条
    # list_per_page = 10

    # list_editable 设置默认可编辑字段
    # list_editable = ['machine_room_id', 'temperature']

    # fk_fields 设置显示外键字段
    # fk_fields = ('machine_room_id',)


class WithDraoMoneyAdmin(object):
    list_display = ['withdraw_no', 'money', 'real_money', 'user', 'receive_way', 'receive_money_info', 'withdraw_status']
    list_filter = ['withdraw_no', 'user', 'add_time', 'receive_time']
    model_icon = 'fa fa-jpy'

    # 搜索
    # search_fields = ['withdraw_status', 'withdraw_no', 'user_msg','full_name']
    # 设置可以在列表中直接修改的字段
    # list_editable = ['withdraw_status', 'receive_time']
    readonly_fields = ['add_time', 'withdraw_no', 'money', 'receive_way', 'receive_account', 'bank_type', 'full_name',
                       'receive_time']
    fields = ['withdraw_status']


class BusinessInfoAdmin(object):
    list_display = ['name', 'c_appid', 'add_time', 'last_time', 'is_active', 'total_money']
    list_filter = ['name', 'c_appid', 'is_active']
    readonly_fields = ['total_money']


xadmin.site.register(OrderInfo, OrderInfoAdmin)
xadmin.site.register(WithDrawMoney, WithDraoMoneyAdmin)
xadmin.site.register(BusinessInfo, BusinessInfoAdmin)
