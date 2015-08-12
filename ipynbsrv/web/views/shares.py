from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from ipynbsrv.core import settings
from ipynbsrv.core.auth.checks import login_allowed
from ipynbsrv.core.models import Share, Tag
from ipynbsrv.web.api_client_proxy import get_httpclient_instance
from ipynbsrv.web.views._messages import api_error_message
from slumber.exceptions import HttpClientError


@user_passes_test(login_allowed)
def index(request):
    """
    Shares listing/index.
    """
    client = get_httpclient_instance(request)
    shares = client.shares.get()
    new_notifications_count = len(client.notificationlogs.unread.get())
    return render(request, 'web/shares/index.html', {
        'title': "Shares",
        'shares': shares,
        'new_notifications_count': new_notifications_count
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

    client = get_httpclient_instance(request)

    # dict to hold all the params to call the api
    params = {}

    params["name"] = request.POST.get('name')
    params["description"] = request.POST.get('description', '')
    params["owner"] = request.user.backend_user.id
    params["access_groups"] = request.POST.getlist('access_groups', [])

    tag_labels = request.POST.get('tags').split(',')

    tags = []
    for tag in tag_labels:
        if tag:
            # see if tag with this label exists already
            try:
                t = client.tags.by_name(tag).get()
            except Exception as e:
                t = None
            if not t:
                # create a new tag
                try:
                    tag_params = {"label": str(tag)}
                    t = client.tags.post(tag_params)
                except Exception as e:
                    messages.error(request, api_error_message(e, tag_params))
                    return redirect('shares')
            else:
                t = t[0]
            tags.append(t.id)

    params["tags"] = tags

    client.shares.get()
    try:
        client.shares.post(params)
        messages.success(request, "Share created sucessfully.")
    except HttpClientError:
        messages.error(request, "Bad Request. A share with this name already exists.")
    except Exception as e:
        messages.error(request, api_error_message(e, params))
    return redirect('shares')


@user_passes_test(login_allowed)
def share_add_access_groups(request):

    """
    Add access groups to the share.
    """
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')
    if 'id' not in request.POST  or not request.POST.get('id').isdigit() or 'access_groups' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('shares')

    access_groups = request.POST.getlist('access_groups')
    share_id = request.POST.get('id')
    client = get_httpclient_instance(request)

    # cannot validate existance of groups due to visibility permissions 
    # i.e. of single_user_groups, let the API handle that
    params = {}
    params['access_groups'] = access_groups

    try:
        client.shares(share_id).add_access_groups.post(params)
        messages.success(request, "The selected groups are now a member of this share.")
    except Exception as e:
        messages.error(request, api_error_message(e, params))

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

    # then call API to add the users to the group
    client.shares.get()
    params = {"access_groups": [group_id]}

    try:
        client.shares(share_id).remove_access_groups.post(params)
        messages.success(request, "The selected groups are now removed from this share.")
    except Exception as e:
        messages.error(request, api_error_message(e, params))
        return(redirect('share_manage', share_id))

    return redirect('share_manage', share_id)


@user_passes_test(login_allowed)
def delete(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')
    if 'share_id' not in request.POST or not request.POST.get('share_id').isdigit():
        messages.error(request, "Invalid POST request.")
        return redirect('shares')

    share_id = int(request.POST.get('share_id'))

    client = get_httpclient_instance(request)
    share = client.shares(share_id).get()

    if share:
        if share.owner.id == request.user.backend_user.id:
            try:
                client.shares(share_id).delete()
                messages.success(request, "Share `{}` deleted sucessfully.".format(share.name))
            except Exception as e:
                messages.error(request, api_error_message(e, ""))
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
    if 'id' not in request.POST or not request.POST.get('id').isdigit():
        messages.error(request, "Invalid POST request.")
        return redirect('shares')

    share_id = int(request.POST.get('id'))

    client = get_httpclient_instance(request)
    share = client.shares(share_id).get()

    params = {"users": [request.user.id]}

    if share:
        if share.owner == request.user.backend_user.id:
            messages.error(request, "You cannot leave an owned share. Please delete it instead.")
        else:
            try:
                client.shares(share_id).remove_users.post(params)
                messages.success(request, "You successfully left the share.")
            except Exception as e:
                messages.error(request, api_error_message(e, params))
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
    share['access_group_ids'] = [g.id for g in share.access_groups]
    users = client.users.get()
    groups = client.collaborationgroups.get()
    new_notifications_count = len(client.notificationlogs.unread.get())

    if share:
            return render(request, 'web/shares/manage.html', {
                'title': "Manage Share",
                'share': share,
                'members': share.members,
                'users': users,
                'groups': groups,
                'new_notifications_count': new_notifications_count
            })
    else:
        messages.error(request, "Share does not exist.")

    return redirect('shares')
