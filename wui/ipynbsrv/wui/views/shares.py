from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from ipynbsrv.wui.auth.checks import login_allowed
from ipynbsrv.wui.models import Share, Tag
from ipynbsrv.wui.signals.signals import (group_modified, share_created, share_user_added, share_user_leaved, share_user_removed)


"""
TODO:
  - randomly fails with id = ''
  - autocompletion in user form input
"""
@user_passes_test(login_allowed)
def adduser(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')

    if not 'id' in request.POST or not 'users' in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('shares')

    id = request.POST.get('id', -1)
    usernames = request.POST.get('users')
    share = Share.objects.filter(pk=id).first()

    if share:
        if share.owner == request.user:
            for username in usernames.split(","):
                user = User.objects.filter(username=username).first()
                if user and not share.is_member(user):
                    share.group.user_set.add(user)
                    group_modified.send(None, group=share.group, fields=None) # should fire by Django
                    share_user_added.send(None, share=share, user=user)

            messages.success(request, "Sucessfully added the new member(s).")
        else:
            messages.error(request, "Not enough permissions to add a new user to that share.")
    else:
        messages.error(request, "Share does not exist.")

    return redirect('shares')


"""
DONE
"""
@user_passes_test(login_allowed)
def index(request):
    user = request.user
    return render(request, 'wui/shares/index.html', {
        'title':  "Shares",
        'shares': Share.for_user(user)
    })


"""
TODO
  - adding tags fails
"""
@user_passes_test(login_allowed)
def create(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')

    if not 'name' in request.POST or not 'description' in request.POST or not 'tags' in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('shares')

    name  = request.POST.get('name')
    desc  = request.POST.get('description', "")
    tags  = request.POST.get('tags', "")
    owner = request.user

    if Share.objects.filter(name=name):
        messages.error(request, "A share with that name already exists.")
    else:
        # creating the share's dedicated group
        group = Group(name="share_" + name)
        group.save()
        group.user_set.add(owner)
        group_modified.send(None, group=group, fields=None) # should fire by Django
        # creating the share itself
        share = Share(name=name, description=desc, owner=owner, group=group)
        share.save()
        # adding tags to the share
        for tag in tags.split(","):
            tag, created = Tag.objects.get_or_create(label=tag)
            if created:
                tag.save()
            share.tags.add(tag)

        messages.success(request, "Share created sucessfully.")

    return redirect('shares')


"""
DONE
"""
@user_passes_test(login_allowed)
def delete(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')

    if not 'id' in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('shares')

    id = request.POST.get('id')
    share = Share.objects.filter(pk=id).first()
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
DONE
"""
@user_passes_test(login_allowed)
def leave(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')

    if not 'id' in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('shares')

    id = request.POST.get('id')
    share = Share.objects.filter(pk=id).first()
    if share:
        if share.owner == request.user:
            messages.error(request, "Cannot leave a managed share.")
        else:
            share.group.user_set.remove(request.user)
            group_modified.send(None, group=share.group, fields=None) # should fire by Django
            share_user_leaved.send(None, share=share, user=request.user)

            messages.success(request, "Successfully leaved the share.")
    else:
        messages.error(request, "Share does not exist.")

    return redirect('shares')


"""
DONE
"""
@user_passes_test(login_allowed)
def manage(request, id):
    if request.method == "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')

    share = Share.objects.filter(pk=id).first()
    if share:
        if share.owner == request.user:
            return render(request, 'wui/shares/manage.html', {
                'title':   "Manage Share",
                'share':   share,
                'members': share.get_members()
            })
        else:
            messages.error(request, "Not enough permissions to manage this share.")
    else:
        messages.error(request, "Share does not exist.")

    return redirect('shares')

"""
TODO:
  - redirect to correct manage page
"""
@user_passes_test(login_allowed)
def remove_user(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')

    if not 'share_id' in request.POST or not 'user_id' in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('shares')

    share_id = request.POST.get('share_id')
    user_id = request.POST.get('user_id')
    share = Share.objects.filter(pk=share_id).first()
    user = User.objects.filter(pk=user_id).first()

    if share:
        if share.owner == request.user:
            if user:
                share.group.user_set.remove(user)
                group_modified.send(None, group=share.group, fields=None) # should fire by Django
                share_user_removed.send(None, share=share, user=user)

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
