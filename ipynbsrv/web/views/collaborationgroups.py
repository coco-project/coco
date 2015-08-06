from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group, User
from django.db import IntegrityError
from django.shortcuts import redirect, render
from ipynbsrv.core.auth.checks import login_allowed
from ipynbsrv.core.models import BackendGroup, Notification
from ipynbsrv.web.api_client_proxy import get_httpclient_instance
from ipynbsrv.web.views._messages import api_error_message


@user_passes_test(login_allowed)
def index(request):
    """
    Groups listing/index.
    """
    client = get_httpclient_instance(request)
    users = client.users.get()
    collab_groups = client.collaborationgroups.get()
    for group in collab_groups:
        group["member_ids"] = [member.id for member in group.members]

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
    members = group.members
    users = client.users.get()
    group["member_ids"] = [member.id for member in members]

    return render(request, 'web/collaborationgroups/manage.html', {
        'title': "Group",
        'group': group,
        'members': members,
        'users': users
    })


@user_passes_test(login_allowed)
def create(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('groups')

    params = {}
    if 'name' not in request.POST:
        messages.error(request, "Invalid POST request.")
    else:
        params["name"] = request.POST.get('name')

    if 'public' in request.POST:
        params["is_public"] = True
    else:
        params["is_public"] = False

    client = get_httpclient_instance(request)

    try:
        # stupid create workaround (see containers)
        client.collaborationgroups.get()
        client.collaborationgroups.post(params)
        messages.success(request, "Group `{}` created sucessfully.".format(params.get("name")))
    except Exception as e:
        messages.error(request, api_error_message(e, params))

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
        try:
            client.collaborationgroups(group_id).delete()
            messages.success(request, "Group `{}` deleted.".format(group.name))
        except Exception as e:
            messages.error(request, api_error_message(e, ""))

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
    user = client.users(user_id).get()

    params = {}
    params["users"] = [user_id]

    if group:
        if request.user.is_superuser or request.user.backend_user.id == group.creator.id or request.user.backend_user.id in group.admins:
            try:
                client.collaborationgroups(group_id).add_admins.post(params)
                messages.success(request, "{} is now a admin of {}.".format(user.username, group.name))
            except Exception as e:
                messages.error(request, api_error_message(e, params))

            request.method = "GET"
            return redirect('group_manage', group.id)
        else:
            messages.error(request, "Not enough permissions to do this.")
        return redirect('group_manage', group.id)
    else:
        messages.error(request, "Group does not exist.")
        return redirect('group_manage', group.id)


@user_passes_test(login_allowed)
def remove_admin(request):
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
    user = client.users(user_id).get()

    params = {}
    params["users"] = [user_id]

    if group:
        if request.user.is_superuser or request.user.backend_user.id == group.creator.id or request.user.backend_user.id in group.admins:
            try:
                client.collaborationgroups(group_id).remove_admins.post(params)
                messages.success(request, "{} is not a admin of {} anymore.".format(user.username, group.name))
            except Exception as e:
                messages.error(request, api_error_message(e, params))

            request.method = "GET"
            return redirect('group_manage', group.id)
        else:
            messages.error(request, "Not enough permissions to do this.")
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

    print(users)

    client = get_httpclient_instance(request)

    user_list = []
    # validate existance of users first
    for u in users:
        user = client.users(u).get()
        if user:
            user_list.append(u)

    # then call API to add the users to the group
    params = {}
    params["users"] = user_list
    try:
        client.collaborationgroups(group_id).add_members.post(params)
        messages.success(request, "Users successfully added to the group.")
    except Exception as e:
        messages.error(request, api_error_message(e, params))

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
            params = {}
            params["users"] = [user_id]
            # API call
            try:
                client.collaborationgroups(group_id).remove_members.post(params)
                messages.success(request, "Sucessfully removed {} from the group.".format(user.username))
            except Exception as e:
                messages.error(request, api_error_message(e, params))

            request.method = "GET"
            return redirect('group_manage', group.id)
        else:
            messages.error(request, "User does not exist.")
            return redirect('group_manage', group.id)
    else:
        messages.error(request, "Group does not exist.")

    return redirect('group_manage', group_id)


@user_passes_test(login_allowed)
def leave(request):
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
            params = {}
            params["users"] = [user_id]
            try:
                client.collaborationgroups(group_id).remove_members.post(params)
                messages.success(request, "You are no longer a member of group {}.".format(group.name))
            except Exception as e:
                messages.error(request, api_error_message(e, params))

            request.method = "GET"
            return redirect('groups')
        else:
            messages.error(request, "User does not exist.")
            return redirect('group_manage', group.id)
    else:
        messages.error(request, "Group does not exist.")

    return redirect('groups')


@user_passes_test(login_allowed)
def join(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')
    if 'group_id' not in request.POST or 'user_id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('groups')

    user_id = request.POST.get('user_id')
    group_id = request.POST.get('group_id')

    client = get_httpclient_instance(request)

    group = client.collaborationgroups(group_id).get()
    user = client.users(user_id).get()
    if user:
        params = {}
        params["users"] = [user_id]
        try:
            client.collaborationgroups(group_id).add_members.post(params)
            messages.success(request, "You are now a member of {}.".format(group.name))
        except Exception as e:
            messages.error(request, api_error_message(e, params))

    return redirect('groups')
