from django.contrib.auth.decorators import login_required
from django.shortcuts import render


""
@login_required
def index(request):
    context = {
        'title': 'Shares'
    }

    return render(request, 'wui/shares.html', context)
