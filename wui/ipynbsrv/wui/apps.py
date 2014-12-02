from django.apps import AppConfig


""
class WuiAppConfig(AppConfig):
    name = 'ipynbsrv.wui'
    verbose_name = 'IPython Notebook Server Web Interface'

    def ready(self):
        import ipynbsrv.wui.signals.handlers
