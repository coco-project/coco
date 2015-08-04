from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group, User
from django.db import IntegrityError
from django.shortcuts import redirect, render
from ipynbsrv.core.auth.checks import login_allowed
from ipynbsrv.core.models import BackendGroup, Notification
from ipynbsrv.web.api_client_proxy import get_httpclient_instance


@user_passes_test(login_allowed)
def index(request):
    """
    Groups listing/index.
    """
    client = get_httpclient_instance(request)
    users = client.users.get()
    collab_groups = client.collaborationgroups.get()

    return render(request, 'web/collaborationgroups/index.html', {
        'title': "Groups",
        'groups': collab_groups,
        'users': users
    })


@user_passes_test(login_allowed)
def manage(request, group_id):
    """
    Manage single group.
    """
    client = get_httpclient_instance(request)
    group = client.collaborationgroups(group_id).get()
    members = group.django_group.user_set
    users = client.users.get()

    return render(request, 'web/collaborationgroups/manage.html', {
        'title': "Group",
        'group': group,
        'members': members,
        'users': users,
    })


@user_passes_test(login_allowed)
def create(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('groups')

    if 'name' not in request.POST:
        messages.error(request, "Invalid POST request.")
    else:
        name = request.POST.get('name')

    public = False
    if 'public' in request.POST:
        public = True

    client = get_httpclient_instance(request)

    # stupid create workaround (see containers)
    client.collaborationgroups.get()
    client.collaborationgroups.post({
        "django_group": {
            "name": name
        }, "is_public": public,
    })

    messages.success(request, "Group `{}` created sucessfully.".format(name))

    return redirect('groups')


@user_passes_test(login_allowed)
def delete(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('groups')
    if 'group_id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('shares')

    group_id = int(request.POST.get('group_id'))

    client = get_httpclient_instance(request)
    group = client.collaborationgroups(group_id).get()
    if group:
        client.collaborationgroups(group_id).delete()
        messages.success(request, "Group `{}` deleted.".format(group.name))

    else:
        messages.error(request, "Group does not exist.")

    return redirect('groups')


@user_passes_test(login_allowed)
def add_admin(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')
    if 'group_id' not in request.POST or 'user_id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('shares')

    group_id = int(request.POST.get('group_id'))
    user_id = int(request.POST.get('user_id'))

    client = get_httpclient_instance(request)
    group = client.collaborationgroups(group_id).get()

    if group:
        if request.user.is_superuser or request.user.backend_user.id == group.creator or request.backend_user in group.admins:
            user = client.users(user_id).get()
            if user and hasattr(user, 'backend_user'):
                client.collaborationgroups(group_id).add_admins.post({
                    "users": [user_id]
                    })
                messages.success(request, "{} is now a admin of {}.".format(user.username, group.name))
                request.method = "GET"
                return redirect('group_manage', group.id)
    else:
        messages.error(request, "Group does not exist.")
        return redirect('group_manage', group.id)


@user_passes_test(login_allowed)
def add_members(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')

    users = request.POST.getlist('users')
    group_id = request.POST.get('group_id')

    client = get_httpclient_instance(request)

    user_list = []
    # validate existance of users first
    for u in users:
        user = client.users(u).get()
    if user:
        user_list.append(u)

    # then call API to add the users to the group
    client = get_httpclient_instance(request)
    client.collaborationgroups(group_id).add_members.post({"users": user_list})

    return redirect('group_manage', group_id)


@user_passes_test(login_allowed)
def remove_member(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('groups')
    if 'group_id' not in request.POST or 'user_id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('groups')

    group_id = int(request.POST.get('group_id'))
    user_id = int(request.POST.get('user_id'))

    client = get_httpclient_instance(request)

    user = client.users(user_id).get()
    group = client.collaborationgroups(group_id).get()

    if group:
        if user:
            client.collaborationgroups(group_id).remove_members.post({
                "users": [user_id]
                })
            messages.success(request, "Sucessfully removed the user from the group.")
            request.method = "GET"
            return redirect('group_manage', group.id)
        else:
            messages.error(request, "User does not exist.")
            return redirect('group_manage', group.id)
    else:
        messages.error(request, "Group does not exist.")

    return redirect('group_manage', group_id)


def notify_group_members(group, message, sender, request):
    """
    Todo: write documentation.
    """
    client = get_httpclient_instance(request)
    client.notifications.post({
        "sender": sender,
        "message": message,
        "event_type": Notification.GROUP,
        "receiving_groups": [group]
        })
