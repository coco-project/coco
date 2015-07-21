from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render
from ipynbsrv.core.auth.checks import login_alloweds


@user_passes_test(login_allowed)
def index(request):
    """
    Shares listing/index.
    """
    return render(request, 'web/groups/index.html', {
        'title': "Groups",
        'groups': request.user.groups.all(),
        'users': User.objects.all()
    })


@user_passes_test(login_allowed)
def create(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('groups')
    if 'name' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('groups')

    

    messages.success(request, "Group created sucessfully.")

    return redirect('groups')
