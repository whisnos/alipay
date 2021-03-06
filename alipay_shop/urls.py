"""alipay_shop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
import xadmin
from user.views import NoticeInfoViewset,ChartInfoViewset, \
    QueryOrderView,receive_post,make_pay
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from user.views import RegisterUserProfileViewset
from trade.views import OrderViewset, AlipayReceiveView, GetPayView, WithDrawViewset, TotalNumViewset, WxpayReceiveView,wx_return
from rest_framework_jwt.views import obtain_jwt_token
from user.views import redirect_url,wx_redirect
route = DefaultRouter()
route.register(r'users', RegisterUserProfileViewset, base_name="users")
route.register(r'orders', OrderViewset, base_name="orders")
route.register(r'drawings',WithDrawViewset,base_name='moneys')
route.register(r'totals', TotalNumViewset, base_name="totals")
route.register(r'notices', NoticeInfoViewset, base_name="notices")
route.register(r'charts', ChartInfoViewset, base_name="charts")
urlpatterns = [
    url(r'^admin/', xadmin.site.urls),
    url(r'^docs/', include_docs_urls(title='API接口文档')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^login', obtain_jwt_token),
    url(r'^', include(route.urls)),
    url(r'^alipay/receive/', AlipayReceiveView.as_view(), name="receive"),
    url(r'^wxpay/receive/', WxpayReceiveView.as_view(), name="receive"),
    url(r'^get_pay/', GetPayView.as_view(), name="get_pay"),
    url(r'^query_order/', QueryOrderView.as_view(), name="query_order"),
    url(r'^redirect_url/', redirect_url, name="redirect_url"),
    url(r'^wx_redirect/', wx_redirect, name="wx_redirect"),
    url(r'^receive_post/', receive_post, name="receive_post"),
    url(r'^make_pay/', make_pay, name="receive_post"),
    url(r'^wx_return/', wx_return, name="wx_return"),
]
