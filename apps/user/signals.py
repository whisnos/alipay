from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from user.models import UserProfile
# User = get_user_model()

# @receiver(post_save, sender=UserProfile)#instance就是UserProfile
# def create_user(sender, instance=None, created=False, **kwargs):
#     print('信号外',instance.password)
#     if created:
#         password = instance.password
#         instance.set_password(password)
#         print('信号途径',instance)
#         instance.save()
