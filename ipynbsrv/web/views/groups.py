from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group, User
from django.shortcuts import redirect, render
from ipynbsrv.core.auth.checks import login_allowed
from ipynbsrv.core.models import BackendGroup, Notification, NotificationReceivers


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

    if 'name' not in request.POST or 'users' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('groups')

    name = request.POST['name']
    users = request.POST.getlist('users')

    try:
        guid = BackendGroup.generate_internal_guid()

        group = Group(name=name)
        group.save()
        be_group = BackendGroup(backend_pk=name, backend_id=guid, django_group=group)
        be_group.save()

        for u in users:
            print(u)
            group.user_set.add(User.objects.get(id=u))

        if 'notify' in request.POST:
            notify_group_members(group, "You have been added to the group {}".format(name), request.user)
            messages.success(request, "Members will get a notification about the group creation")

        messages.success(request, "Group `{}` created sucessfully.".format(name))

    #except IntegrityError:
    #    messages.error(request, "Name already in use. Please choose another one.")
    except Exception as e:
        try:
            group.delete()
        except:
            pass
        # TODO: nice error & rollback
        raise e

    return redirect('groups')


def notify_group_members(group, message, sender):
    n = Notification(sender=sender, message=message, event_type=Notification.GROUP)
    n.save()
    nr = NotificationReceivers(notification=n, receiving_group=group)
    nr.save()

    n.send()
