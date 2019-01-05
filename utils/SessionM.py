from importlib import import_module

from django.utils.deprecation import MiddlewareMixin
from rest_framework_jwt.utils import jwt_decode_handler
from alipay_shop import settings


class SessionMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        self.get_response = get_response
        # engine = import_module(settings.SESSION_ENGINE)
        # self.SessionStore = engine.SessionStore

    def process_request(self, request):
        request.session['token'] = request.META.get('HTTP_TOKEN')

        # print(request.session.get('token'))
