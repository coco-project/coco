from django.dispatch import receiver
from ipynbsrv.wui.signals.signals import *


""
@receiver(user_logged_in)
def user_logged_in(sender, **kwargs):
    print("Received user_logged_in signal.")


""
@receiver(user_logged_out)
def user_logged_out(sender, **kwargs):
    print("Received user_logged_out signal.")
