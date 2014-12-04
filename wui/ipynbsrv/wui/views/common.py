from django.contrib.auth.decorators import login_required
from django.shortcuts import render


""
@login_required
def dashboard(request):
    context = {
        'title': 'Dashboard'
    }

    return render(request, 'wui/dashboard.html', context)
