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
    Create a new share.
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
    tag_labels = request.POST.get('tags').split(',')
    owner = request.user.backend_user.id
    access_groups = request.POST.getlist('access_groups', [])

    client = get_httpclient_instance(request)

    tags = []
    for tag in tag_labels:
        # see if tag with this label exists already
        t = client.tags(tag).get()
        if not t:
            # create a new tag
            t = client.tags.get()
            t = client.tags.post({ "label": str(tag) })
        else:
            t = t[0]
        tags.append(t.id)

    client.shares.get()
    client.shares.post(data={
        "name": name,
        "description": desc,
        "owner": owner,
        "access_groups": access_groups,
        "tags": tags
    })
    messages.success(request, "Share created sucessfully.")
    return redirect('shares')


@user_passes_test(login_allowed)
def share_add_access_groups(request):

    """
    Add access groups to the share.
    """
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')
    if 'id' not in request.POST or 'access_groups' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('shares')

    access_groups = request.POST.getlist('access_groups')
    share_id = request.POST.get('id')
    client = get_httpclient_instance(request)
    notify = request.POST.get('notify')
    print("views: " + str(notify))
    group_list = []
    # validate existance of users first
    for group_id in access_groups:
        access_group = client.collaborationgroups(group_id).get()
    if access_group:
        group_list.append(group_id)

    print(group_list)
    params = {}
    params['access_groups'] = group_list
    if notify:
        params['notify'] = True
    print(params)
    # then call API to add the users to the group
    client.shares.get()
    client.shares(share_id).add_access_groups.post(params)
    messages.success(request, "Access permission successfully added.")

    return redirect('share_manage', share_id)


@user_passes_test(login_allowed)
def share_remove_access_group(request):

    """
    Add access groups to the share.
    """
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')
    if 'share_id' not in request.POST or 'access_group' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('shares')

    group_id = request.POST.get('access_group')
    share_id = request.POST.get('share_id')
    client = get_httpclient_instance(request)

    access_group = client.collaborationgroups(group_id).get()
    if not access_group:
        messages.error("Collaboration Group not found.")
        return redirect('share_manage', group_id)

    # then call API to add the users to the group
    client.shares.get()
    client.shares(share_id).remove_access_groups.post({"access_groups": [group_id]})

    messages.success(request, "Access permission successfully removed.")
    return redirect('share_manage', share_id)


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
    groups = client.collaborationgroups.get()

    if share:
            return render(request, 'web/shares/manage.html', {
                'title': "Manage Share",
                'share': share,
                'members': share.members,
                'users': users,
                'groups': groups
            })
    else:
        messages.error(request, "Share does not exist.")

    return redirect('shares')
