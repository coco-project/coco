from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from ipynbsrv.wui.models import User, Share, Tag
from ipynbsrv.wui.signals.signals import share_accepted, share_declined, share_invited, share_leaved, share_user_added


""
@login_required
def adduser(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')

    # TODO: check if user is owner of share
    # id = share id; user = username
    # add user to group

    if not 'id' in request.POST or not 'user' in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('shares')

    share = request.POST.get('id')
    user  = request.POST.get('user')
    share = Share.objects.get(id=share)

    share_user_added.send(None, share=share, user=user)
    messages.success(request, "User '{0}' added successfully to share '{1}'.".format(user, share.name))

    return redirect('shares')


""
@login_required
def index(request):
    # TODO: filter user account
    shares = Share.objects.filter(owner=request.user.get_full_name())
    return render(request, 'wui/shares/index.html', {
        'title':  "Shares",
        'shares': shares
    })


""
@login_required
def accept(request):
    # ansure user is allowed to accept
    # add user to group of share
    share_accepted.send(None, share="", user=request.user)
    return render(request, 'wui/shares/index.html', {})


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
    owner = request.user.get_full_name()

    try:
        share = Share(name=name, description=desc, owner=owner, group="")
        share.save()

        tags = tags.split(", ")
        for tag in tags:
            tag = Tag(label=tag)
            tag.save()
            share.tags.add(tag)

        messages.success(request, "Share '{0}' created sucessfully.".format(name))
    except:
        messages.error(request, "Error creating the '{0}' share.".format(name))

    return redirect('shares')


""
@login_required
def decline(request):
    share_declined.send(None, share="", user=request.user)
    return render(request, 'wui/shares/index.html', {})


"Deletes the share specified by POST[name]"
@login_required
def delete(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('shares')

    if not 'id' in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('shares')

    id    = request.POST.get('id')
    share = Share.objects.get(id=id)
    # check if is owner
    # remove share from other members
    try:
        share.delete()
        messages.success(request, "Share '{0}' deleted sucessfully.".format(share.name))
    except:
        messages.error(request, "Error deleting the '{0}' share.".format(share.name))

    return redirect('shares')


""
@login_required
def invite(request):
    share_invited.send(None, share="", user=request.user)
    return render(request, 'wui/shares/index.html', {})


""
@login_required
def leave(request):
    share_leaved.send(None, share="", user=request.user)
    return render(request, 'wui/shares/index.html', {})


""
@login_required
def manage(request, id):
    share = Share.objects.get(id=id)

    return render(request, 'wui/shares/manage.html', {
        'title': "Share :: {0}".format(share.name),
        'share': share
    })
