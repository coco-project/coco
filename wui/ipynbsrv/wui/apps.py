from django import apps


class AppConfig(apps.AppConfig):
    name = 'ipynbsrv.wui'
    verbose_name = 'IPython Notebook Server Web Interface'

    def ready(self):
        # import ipynbsrv.wui.signals.containers
        import ipynbsrv.wui.signals.groups
        import ipynbsrv.wui.signals.images
        import ipynbsrv.wui.signals.shares
        import ipynbsrv.wui.signals.users
