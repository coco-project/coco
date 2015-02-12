from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from ipynbsrv.wui.auth.checks import login_allowed
from ipynbsrv.wui.models import Share, Tag


@user_passes_test(login_allowed)
def add_user(request):
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
    usernames = request.POST.get('users')
    origin = request.POST.get('origin', None)

    share = Share.objects.filter(pk=share_id)
    if share.exists():
        share = share.first()
        if share.owner == request.user:
            for user in usernames.split(","):
                user = User.objects.filter(username=user)
                if user.exists() and not share.is_member(user.first()):
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

    if Share.objects.filter(name=name).exists():
        messages.error(request, "A share with that name already exists.")
    else:
        # creating the share's dedicated group
        group = Group(name=settings.SHARE_GROUP_PREFIX + name)
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


@user_passes_test(login_allowed)
def delete(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')
    if 'id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('shares')

    share_id = int(request.POST.get('id'))

    share = Share.objects.filter(pk=share_id)
    if share.exists():
        share = share.first()
        if share.owner == request.user:
            share.delete()
            messages.success(request, "Share deleted sucessfully.")
        else:
            messages.error(request, "You don't have enough permissions for the requested operation.")
    else:
        messages.error(request, "Share does not exist.")

    return redirect('shares')


@user_passes_test(login_allowed)
def index(request):
    """
    Shares listing/index.
    """
    return render(request, 'wui/shares/index.html', {
        'title': "Shares",
        'shares': Share.for_user(request.user)
    })


@user_passes_test(login_allowed)
def leave(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')
    if 'id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('shares')

    share_id = int(request.POST.get('id'))

    share = Share.objects.filter(pk=share_id)
    if share.exists():
        share = share.first()
        if share.owner == request.user:
            messages.error(request, "You cannot leave an owned share. Please delete it instead.")
        else:
            share.group.user_set.remove(request.user)
            messages.success(request, "You successfully leaved the share.")
    else:
        messages.error(request, "Share does not exist.")

    return redirect('shares')


@user_passes_test(login_allowed)
def manage(request, share_id):
    if request.method == "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')

    share = Share.objects.filter(pk=share_id)
    if share.exists():
        share = share.first()
        if share.owner == request.user:
            return render(request, 'wui/shares/manage.html', {
                'title': "Manage Share",
                'share': share,
                'members': share.get_members()
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
