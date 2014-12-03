from django.apps import AppConfig


""
class WuiAppConfig(AppConfig):
    name = 'ipynbsrv.wui'
    verbose_name = 'IPython Notebook Server Web Interface'

    def ready(self):
        import ipynbsrv.wui.signals.common_handlers
        import ipynbsrv.wui.signals.container_handlers
        import ipynbsrv.wui.signals.image_handlers
        import ipynbsrv.wui.signals.share_handlers
