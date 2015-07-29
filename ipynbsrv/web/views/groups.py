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

    # Todo: fix api/users/ permissions
    # Todo: possibility to get groups by user

    return render(request, 'web/groups/index.html', {
        'title': "Groups",
        'groups': request.user.groups.all(),
        'users': User.objects.all()
    })


@user_passes_test(login_allowed)
def manage(request, group_id):
    """
    Manage single group.
    """
    group = Group.objects.get(id=group_id)
    return render(request, 'web/groups/manage.html', {
        'title': "Group",
        'group': group,
        'members': group.user_set.all()
    })


@user_passes_test(login_allowed)
def create(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('groups')

    if 'name' not in request.POST or 'users' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('groups')

    name = request.POST['name']
    users = request.POST.getlist('users')

    try:
        guid = BackendGroup.generate_internal_guid()

        group = Group(name=name)
        group.save()
        be_group = BackendGroup(
            backend_pk=name,
            backend_id=guid,
            django_group=group,
            creator=request.user
        )
        be_group.save()
        be_group.admins.add(request.user)
        be_group.save()

        for u in users:
            user = User.objects.filter(id=u)
            if user is not None:
                print(u)
                group.user_set.add(user.first())

    except IntegrityError:
        messages.error(request, "Name already in use. Please choose another one.")
    except Exception as e:
        try:
            be_group.delete()
        except:
            pass
        # TODO: nice error & rollback
        raise e

    if 'notify' in request.POST:
        notify_group_members(
            group=group,
            message="You have been added to the group {}".format(name),
            sender=request.user
        )
        messages.success(request, "Members will get a notification about the group creation")

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

    group = Group.objects.filter(pk=group_id)
    if group.exists():
        group = group.first()
        if group.backend_group.creator == request.user or request.user in group.backend_group.admins.all():
            group.delete()
            messages.success(request, "Sucessfully deleted group.")
            request.method = "GET"
            return redirect('groups')
        else:
            messages.error(request, "You don't have enough permissions for the requested operation.")
            return redirect('groups')
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

    group = Group.objects.filter(pk=group_id)
    if group.exists():
        group = group.first()
        if group.backend_group.creator == request.user or request.user in group.backend_group.admins.all():
            user = User.objects.filter(pk=user_id)
            if user.exists():
                group.backend_group.admins.add(user.first())
                messages.success(request, "Sucessfully added user to group admins.")
                request.method = "GET"
                return redirect('group_manage', group.id)
            else:
                messages.error(request, "User does not exist.")
        else:
            messages.error(request, "You don't have enough permissions for the requested operation.")
            return redirect('group_manage', group.id)
    else:
        messages.error(request, "Group does not exist.")

    return redirect('groups')


@user_passes_test(login_allowed)
def remove_user(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')
    if 'group_id' not in request.POST or 'user_id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('shares')

    group_id = int(request.POST.get('group_id'))
    user_id = int(request.POST.get('user_id'))

    group = Group.objects.filter(pk=group_id)
    if group.exists():
        group = group.first()
        if group.backend_group.creator == request.user or request.user in group.backend_group.admins.all() or request.user.id == user_id:
            user = User.objects.filter(pk=user_id)
            if user.exists():
                group.user_set.remove(user.first())
                messages.success(request, "Sucessfully removed the user from the group.")
                request.method = "GET"
                return redirect('group_manage', group.id)
            else:
                messages.error(request, "User does not exist.")
        else:
            messages.error(request, "You don't have enough permissions for the requested operation.")
            return redirect('group_manage', group.id)
    else:
        messages.error(request, "Group does not exist.")

    return redirect('groups')


def notify_group_members(group, message, sender):
    n = Notification(sender=sender, message=message, event_type=Notification.GROUP)
    n.save()
    nr = NotificationReceivers(notification=n, receiving_group=group)
    nr.save()

    n.send()
