from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from ipynbsrv.core import settings
from ipynbsrv.core.auth.checks import login_allowed
from ipynbsrv.core.models import Share, Tag
from ipynbsrv.web.api_client_proxy import get_httpclient_instance


@user_passes_test(login_allowed)
def index(request):
    """
    Shares listing/index.
    """
    client = get_httpclient_instance(request)
    shares = client.shares.get()
    return render(request, 'web/shares/index.html', {
        'title': "Shares",
        'shares': shares
    })


@user_passes_test(login_allowed)
def create(request):
    """
    Todo: get tags
    """
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')
    if 'name' not in request.POST or 'description' not in request.POST or 'tags' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('shares')

    name = request.POST.get('name')
    desc = request.POST.get('description', '')
    # Todo: get tags properly
    tags = request.POST.getlist('tags', [])
    owner = request.user.backend_user.id
    access_groups = request.POST.getlist('access_groups', [])

    client = get_httpclient_instance(request)
    # Todo: check if name already taken
    #if Share.objects.filter(name=name).exists():
    #    messages.error(request, "A share with that name already exists.")

    client.shares.get()
    client.shares.post(data={
        "name": name,
        "description": desc,
        "owner": owner,
        "access_groups": access_groups,
        "tags": []
    })
    messages.success(request, "Share created sucessfully.")
    return redirect('shares')


@user_passes_test(login_allowed)
def add_user(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')
    if 'id' not in request.POST or 'users' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('shares')

    users = request.POST.getlist('users')
    share_id = request.POST.get('id')
    client = get_httpclient_instance(request)

    user_list = []
    # validate existance of users first
    for u in users:
        user = client.users(u).get()
    if user:
        user_list.append(u)

    # then call API to add the users to the group
    client = get_httpclient_instance(request)
    client.shares(share_id).add_users.post({"users": user_list})

    return redirect('group_manage', group_id)


    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')
    if 'id' not in request.POST or 'users' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('shares')

    try:
        share_id = int(request.POST.get('id'))
    except ValueError:
        share_id = -1

    user_ids = request.POST.get('users')
    origin = request.POST.get('origin', None)

    client = get_httpclient_instance(request)
    share = client.shares(share_id).get()

    if share:
        if share.owner == request.user.backend_user.id:
            for user in user_ids.split(","):
                user = User.objects.filter(username=user)
                if user.exists() and not share.user_is_member(user.first()):
                    share.group.user_set.add(user.first())
            messages.success(request, "Sucessfully added the new member(s) to the share.")
        else:
            messages.error(request, "You don't have enough permissions for the requested operation.")
    else:
        messages.error(request, "Share does not exist.")

    if origin:
        request.method = "GET"
        return redirect('share_manage', share.id)

    return redirect('shares')


@user_passes_test(login_allowed)
def delete(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')
    if 'id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('shares')

    share_id = int(request.POST.get('id'))

    client = get_httpclient_instance(request)
    share = client.shares(share_id).get()

    if share:
        if share.owner == request.user.backend_user.id:
            client.shares(share_id).delete()
            messages.success(request, "Share deleted sucessfully.")
        else:
            messages.error(request, "You don't have enough permissions for the requested operation.")
    else:
        messages.error(request, "Share does not exist.")

    return redirect('shares')


@user_passes_test(login_allowed)
def leave(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')
    if 'id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('shares')

    share_id = int(request.POST.get('id'))

    client = get_httpclient_instance(request)
    share = client.shares(share_id).get()
    if share:
        if share.owner == request.user.backend_user.id:
            messages.error(request, "You cannot leave an owned share. Please delete it instead.")
        else:
            client.shares(share_id).remove_users.post({
                "users": [request.user.id]
                })
            messages.success(request, "You successfully left the share.")
    else:
        messages.error(request, "Share does not exist.")

    return redirect('shares')


@user_passes_test(login_allowed)
def manage(request, share_id):
    if request.method == "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')

    client = get_httpclient_instance(request)
    share = client.shares(share_id).get()
    users = client.users.get()
    if share:
        if share.owner == request.user.backend_user.id:
            return render(request, 'web/shares/manage.html', {
                'title': "Manage Share",
                'share': share,
                'members': share.members,
                'users': users
            })
        else:
            messages.error(request, "You don't have enough permissions for the requested operation.")
    else:
        messages.error(request, "Share does not exist.")

    return redirect('shares')


@user_passes_test(login_allowed)
def remove_user(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')
    if 'share_id' not in request.POST or 'user_id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('shares')

    share_id = int(request.POST.get('share_id'))
    user_id = int(request.POST.get('user_id'))

    client = get_httpclient_instance(request)
    share = client.shares(share_id).get()
    if share:
        if share.owner == request.user.backend_user.id:
            messages.error(request, "You cannot leave an owned share. Please delete it instead.")
        else:
            client.shares(share_id).remove_users.post({
                "users": [request.user.id]
                })
            messages.success(request, "You successfully left the share.")
    else:
        messages.error(request, "Share does not exist.")

    return redirect('shares')

    share = Share.objects.filter(pk=share_id)
    if share.exists():
        share = share.first()
        if share.owner == request.user:
            user = User.objects.filter(pk=user_id)
            if user.exists():
                share.group.user_set.remove(user.first())
                messages.success(request, "Sucessfully removed the user from the share.")
                request.method = "GET"
                return redirect('share_manage', share.id)
            else:
                messages.error(request, "User does not exist.")
        else:
            messages.error(request, "You don't have enough permissions for the requested operation.")
    else:
        messages.error(request, "Share does not exist.")

    return redirect('shares')
