from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ipynbsrv.wui.signals.signals import user_logged_in


""
@login_required
def dashboard(request):
    context = {
        'title': 'Dashboard'
    }
    user_logged_in.send_robust(sender=None, user=None)

    return render(request, 'wui/dashboard.html', context)
