from django.apps import AppConfig


class TradeConfig(AppConfig):
    name = 'trade'
    verbose_name = '订单管理'

    def ready(self):
        import trade.signals