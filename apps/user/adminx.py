import xadmin
from xadmin import views
from .models import NoticeInfo, UserProfile
from django.contrib.auth.models import AbstractUser

# Register your models here.
class BaseThemSet(object):
    enable_themes = True
    use_bootswatch = True

class CommSetting(object):
    site_title = '章鱼猫管理后台'
    site_footer = '章鱼猫网络'
    # menu_style = 'accordion'
class NoticeInfoAdmin(object):
    list_display = ['title', 'add_time']

class UserProfileAdmin(object):
    list_display=['username','total_money','is_active']
    readonly_fields = ['total_money','password','add_time','date_joined','last_login']

xadmin.site.register(views.BaseAdminView,BaseThemSet)
xadmin.site.register(views.CommAdminView,CommSetting)
xadmin.site.register(NoticeInfo,NoticeInfoAdmin)

xadmin.site.unregister(UserProfile)
xadmin.site.register(UserProfile, UserProfileAdmin)