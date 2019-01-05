from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from trade.models import WithDrawMoney
from datetime import datetime


# User = get_user_model()

@receiver(post_save, sender=WithDrawMoney)  # instance就是UserProfile
def create_user(sender, instance=None, **kwargs):
    if instance.withdraw_status == '1' and instance.freeze_money != 0:
        instance.freeze_money = 0
        instance.receive_time = datetime.now()
        instance.user.save()
        instance.save()

    # if instance.withdraw_status == '2' and instance.default_flag == False:
    #     money = (instance.money / (1 - instance.user.service_rate))
    #     instance.user.total_money += money
    #     instance.freeze_money = 0
    #     instance.default_flag = True
    #     instance.user.save()
    #     instance.save()
    #     print('回退用户成功',money)
    # elif instance.withdraw_status == '0' and instance.freeze_money != 0:
    #     print('0信号处理 提现失败 返还处理')
    #     instance.freeze_money = (instance.money / (1 - instance.user.service_rate))
    #     instance.save()
    #     instance.user.save()

    # elif instance.withdraw_status == '3' and instance.freeze_money == 0 and instance.money_flag == False:
    #     print('3 提现失败 误操作 返还处理')
    #     instance.user.total_money += (instance.money / (1 - instance.user.service_rate))
    #     instance.user.save()
    #     instance.money_flag = True
    #     instance.save()

    # elif instance.withdraw_status == '0' and instance.freeze_money == 0:
    #     print('4 申请中 误操作')
    #     # instance.user.total_money -= (instance.money / (1 - instance.user.service_rate))
    #     instance.freeze_money = (instance.money / (1 - instance.user.service_rate))
    #     instance.save()
    #     # instance.user.save()
