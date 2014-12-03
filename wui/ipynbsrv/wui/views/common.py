from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ipynbsrv.wui.signals.signals import user_logged_in
from ipynbsrv.wui.tools.filesystem import ensure_directory


""
@login_required
def dashboard(request):
    context = {
        'title': 'Dashboard'
    }
    user_logged_in.send_robust(sender=None, user=None)
    ensure_directory(directory='/Volumes/Macintosh HD2/workspace/FHNW/ipynbsrv/test/test', recursive=True)

    return render(request, 'wui/dashboard.html', context)
