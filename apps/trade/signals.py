from django.db.models.signals import post_save
from django.dispatch import receiver
from trade.models import WithDrawMoney
from datetime import datetime


@receiver(post_save, sender=WithDrawMoney)  # instance就是UserProfile
def create_user(sender, instance=None, **kwargs):
    if instance.withdraw_status == '1' and instance.freeze_money != 0:
        instance.freeze_money = 0
        instance.receive_time = datetime.now()
        instance.user.save()
        instance.save()
