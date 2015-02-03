from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from ipynbsrv.wui.auth.checks import login_allowed
from ipynbsrv.wui.models import Share, Tag


SHARE_GROUP_PREFIX = 'share_'


"""
POST only view to be used as POST action by forms trying to add
new members to a share.

URI: /share/add_user
"""
@user_passes_test(login_allowed)
def add_user(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')

    if 'id' not in request.POST or 'users' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('shares')

    share_id = int(request.POST.get('id'))
    usernames = request.POST.get('users')
    origin = request.POST.get('origin', None)
    share = Share.objects.filter(pk=share_id).first()

    if share:
        if share.owner == request.user:
            for username in usernames.split(","):
                user = User.objects.filter(username=username).first()
                if user and not share.is_member(user):
                    share.group.user_set.add(user)
            messages.success(request, "Sucessfully added the new member(s).")
        else:
            messages.error(request, "Not enough permissions to add a new user to that share.")
    else:
        messages.error(request, "Share does not exist.")

    if origin:
        request.method = "GET"
        return redirect('share_manage', share.id)

    return redirect('shares')


"""
Shares listing/index.

URI: /shares/
"""
@user_passes_test(login_allowed)
def index(request):
    return render(request, 'wui/shares/index.html', {
        'title': "Shares",
        'shares': Share.for_user(request.user)
    })


"""
POST only view to be used as POST action by forms trying
to create a new share.

URI: /share/create
"""
@user_passes_test(login_allowed)
def create(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')

    if 'name' not in request.POST or 'description' not in request.POST or 'tags' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('shares')

    name = request.POST.get('name')
    desc = request.POST.get('description', '')
    tags = request.POST.get('tags', '')
    owner = request.user

    if Share.objects.filter(name=name):
        messages.error(request, "A share with that name already exists.")
    else:
        # creating the share's dedicated group
        group = Group(name=SHARE_GROUP_PREFIX + name)
        group.save()
        group.user_set.add(owner)
        # creating the share itself
        share = Share(name=name, description=desc, owner=owner, group=group)
        share.save()
        # adding tags to the share
        for tag in tags.split(','):
            tag, created = Tag.objects.get_or_create(label=tag)
            if created:
                tag.save()
            share.tags.add(tag)
        messages.success(request, "Share created sucessfully.")

    return redirect('shares')


"""
POST only view to be used as POST action by forms trying
to delete a share.

URI: /share/delete
"""
@user_passes_test(login_allowed)
def delete(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')

    if 'id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('shares')

    share_id = int(request.POST.get('id'))
    share = Share.objects.filter(pk=share_id).first()

    if share:
        if share.owner == request.user:
            share.delete()
            messages.success(request, "Share deleted sucessfully.")
        else:
            messages.error(request, "Not enough permissions to delete this share.")
    else:
        messages.error(request, "Share does not exist.")

    return redirect('shares')


"""
POST only view to be used by forms trying
to remove a user from a share.

URI: /share/leave
"""
@user_passes_test(login_allowed)
def leave(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')

    if 'id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('shares')

    share_id = int(request.POST.get('id'))
    share = Share.objects.filter(pk=share_id).first()

    if share:
        if share.owner == request.user:
            messages.error(request, "Cannot leave an owned share. Delete it instead.")
        else:
            share.group.user_set.remove(request.user)
            messages.success(request, "Successfully leaved the share.")
    else:
        messages.error(request, "Share does not exist.")

    return redirect('shares')


"""
Share detail/manage page.

URI: /share/manage/<id>
"""
@user_passes_test(login_allowed)
def manage(request, share_id):
    if request.method == "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')

    share = Share.objects.filter(pk=share_id).first()

    if share:
        if share.owner == request.user:
            return render(request, 'wui/shares/manage.html', {
                'title': "Manage Share",
                'share': share,
                'members': share.get_members()
            })
        else:
            messages.error(request, "Not enough permissions to manage this share.")
    else:
        messages.error(request, "Share does not exist.")

    return redirect('shares')


"""
POST only view to be used by forms trying
to remove a user from a share.

URI: /share/remove_user
"""
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
    share = Share.objects.filter(pk=share_id).first()
    user = User.objects.filter(pk=user_id).first()

    if share:
        if share.owner == request.user:
            if user:
                share.group.user_set.remove(user)
                messages.success(request, "Removed used from share.")
                request.method = "GET"
                return redirect('share_manage', share.id)
            else:
                messages.error(request, "User does not exist.")
        else:
            messages.error(request, "Not enough permissions for that.")
    else:
        messages.error(request, "Share does not exist.")

    return redirect('shares')
