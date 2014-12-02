from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ipynbsrv.wui.signals.signals import example_signal


""
@login_required
def dashboard(request):
    context = {
        'title': 'Dashboard'
    }

    example_signal.send_robust(None, providing_args=['arg1', 'arg2'])

    return render(request, 'wui/dashboard.html', context)
