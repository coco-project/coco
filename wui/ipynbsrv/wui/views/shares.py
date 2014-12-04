from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from ipynbsrv.wui.models import Share, Tag
from ipynbsrv.wui.signals.signals import share_user_added, share_user_removed


""
@login_required
def adduser(request):
    # if request.method != "POST":
    #     messages.error(request, "Invalid request method.")
    #     return redirect('shares')

    # if not 'id' in request.POST or not 'users' in request.POST:
    #     messages.error(request, "Invalid POST request.")
    #     return redirect('shares')

    # user = LdapUser.for_user(request.user)
    # usernames = request.POST.get('users', "")
    # share = Share.objects.filter(id=request.POST.get('id'))

    # if share:
    #     share = share[0]
    #     if share.owner == user:
    #         for username in usernames.split(","):
    #             luser = LdapUser.objects.filter(username=username)
    #             if luser:
    #                 luser = luser[0]
    #                 # TODO: add user to group if not already member
    #                 share_user_added.send(None, share=share, user=luser)

    #         messages.success(request, "Sucessfully added the new member(s).")
    #     else:
    #         messages.error(request, "Not enough permissions to add a new user to that share.")
    # else:
    #     messages.error(request, "Share does not exist.")

    return redirect('shares')


""
@login_required
def index(request):
    user = request.user
    return render(request, 'wui/shares/index.html', {
        'title':  "Shares",
        'shares': Share.for_user(user)
    })


# ""
# @login_required
# def accept(request):
#     share_accepted.send(None, share="", user=request.user)
#     return render(request, 'wui/shares/index.html', {})


""
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
        group = Group(name=name)
        group.save()
        group.user_set.add(owner)

        share = Share(name=name, description=desc, owner=owner, group=group)
        share.save()
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


# ""
# @login_required
# def decline(request):
#     share_declined.send(None, share="", user=request.user)
#     return render(request, 'wui/shares/index.html', {})


""
@login_required
def delete(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')

    if not 'id' in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('shares')

    id = request.POST.get('id')
    share = Share.objects.filter(id=id)
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


# ""
# @login_required
# def invite(request):
#     share_invited.send(None, share="", user=request.user)
#     return render(request, 'wui/shares/index.html', {})


"DONE"
@login_required
def leave(request):
    # if request.method != "POST":
    #     messages.error(request, "Invalid request method.")
    #     return redirect('shares')

    # if not 'id' in request.POST:
    #     messages.error(request, "Invalid POST request.")
    #     return redirect('shares')

    # id = request.POST.get('id')
    # share = Share.objects.filter(id=id)
    # if share:
    #     if share[0].owner == request.user:
    #         messages.error(request, "Cannot leave a managed share.")
    #     else:
    #         share = share[0]
    #         # TODO: remove user from share group
    #         messages.success(request, "Successfully leaved the share.")
    # else:
    #     messages.error(request, "Share does not exist.")

    return redirect('shares')


""
@login_required
def manage(request, id):
    # if request.method == "POST":
    #     messages.error(request, "Invalid request method.")
    #     return redirect('shares')

    # share = Share.objects.filter(id=id)
    # if share:
    #     if share[0].owner == request.user:
    #         return render(request, 'wui/shares/manage.html', {
    #             'title': "Manage Share",
    #             'share': share[0]
    #         })
    #     else:
    #         messages.error(request, "Not enough permissions to manage this share.")
    # else:
    #     messages.error(request, "Share does not exist.")

    return redirect('shares')
