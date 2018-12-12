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
# from django.contrib import admin
from user.views import index, page2, page1
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from user.views import RegisterUserProfileViewset
from rest_framework_jwt.views import obtain_jwt_token
route = DefaultRouter()
route.register(r'users',RegisterUserProfileViewset)
urlpatterns = [
	# url(r'^admin/', admin.site.urls),
	url(r'^page1/', page1),
	# url(r'^$', index),
	url(r'^page2/', page2),
	url(r'^docs/', include_docs_urls(title='接口文档')),
	url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
	url(r'^login',obtain_jwt_token),
	url(r'^', include(route.urls)),
]
