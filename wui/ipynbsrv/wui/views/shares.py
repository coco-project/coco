from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from ipynbsrv.wui.models import Share, Tag
from ipynbsrv.wui.signals.signals import share_created, share_user_added, share_user_leaved, share_user_removed


"""
TODO:
  - randomly fails with id = ''
  - autocompletion in user form input
"""
@login_required
def adduser(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')

    if not 'id' in request.POST or not 'users' in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('shares')

    id = request.POST.get('id')
    usernames = request.POST.get('users')
    share = Share.objects.filter(pk=id)

    if share:
        share = share[0]
        if share.owner == request.user:
            for username in usernames.split(","):
                user = User.objects.filter(username=username)
                if user:
                    user = user[0]
                    share.group.user_set.add(user)
                    share_user_added.send(None, share=share, user=user)
            share.group.save()

            messages.success(request, "Sucessfully added the new member(s).")
        else:
            messages.error(request, "Not enough permissions to add a new user to that share.")
    else:
        messages.error(request, "Share does not exist.")

    return redirect('shares')


"""
DONE
"""
@login_required
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
@login_required
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
        group.save()

        # creating the share itself
        share = Share(name=name, description=desc, owner=owner, group=group)
        share.save()

        # adding tags to the share
        if tags:
            for tag in tags.split(","):
                tag = Tag.objects.filter(label=tag)
                if tag:
                    tag = tag[0]
                else:
                    tag = Tag(label=tag)
                    tag.save()
                share.tags.add(tag)

        messages.success(request, "Share created sucessfully.")

    return redirect('shares')


"""
DONE
"""
@login_required
def delete(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')

    if not 'id' in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('shares')

    id = request.POST.get('id')
    share = Share.objects.filter(pk=id)
    if share:
        share = share[0]
        if share.owner == request.user:
            group = share.group
            share.delete()
            group.delete()
            messages.success(request, "Share deleted sucessfully.")
        else:
            messages.error(request, "Not enough permissions to delete this share.")
    else:
        messages.error(request, "Share does not exist.")

    return redirect('shares')


"""
DONE
"""
@login_required
def leave(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')

    if not 'id' in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('shares')

    id = request.POST.get('id')
    share = Share.objects.filter(pk=id)
    if share:
        if share[0].owner == request.user:
            messages.error(request, "Cannot leave a managed share.")
        else:
            share = share[0]
            share.group.user_set.remove(request.user)
            share.group.save()
            share_user_leaved.send(None, share=share, user=request.user)

            messages.success(request, "Successfully leaved the share.")
    else:
        messages.error(request, "Share does not exist.")

    return redirect('shares')


"""
DONE
"""
@login_required
def manage(request, id):
    if request.method == "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')

    share = Share.objects.filter(pk=id)
    if share:
        share = share[0]
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
@login_required
def remove_user(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')

    if not 'share_id' in request.POST or not 'user_id' in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('shares')

    share_id = request.POST.get('share_id')
    user_id = request.POST.get('user_id')
    share = Share.objects.filter(pk=share_id)
    user = User.objects.filter(pk=user_id)

    if share:
        share = share[0]
        if share.owner == request.user:
            if user:
                user = user[0]
                share.group.user_set.remove(user)
                share.group.save()

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
