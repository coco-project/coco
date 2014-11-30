from django.shortcuts import render


def containers(request):
    context = {}
    return render(request, 'wui/containers.html', context)

def dashboard(request):
    context = {}
    return render(request, 'wui/dashboard.html', context)

def login(request):
    context = {}
    return render(request, 'wui/login.html', context)

def images(request):
    context = {}
    return render(request, 'wui/images.html', context)

def shares(request):
    context = {}
    return render(request, 'wui/shares.html', context)
