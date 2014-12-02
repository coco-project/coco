from django.dispatch import receiver
from ipynbsrv.wui.signals.signals import example_signal


""
@receiver(example_signal)
def logged_in(sender, **kwargs):
    print("Signal received!")
