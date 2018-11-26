from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class EjNotificationsConfig(AppConfig):
    name = 'ej_notifications'
    verbose_name = _('Notifications')
    signals = None

    def ready(self):
        from . import signals
        self.signals = signals
