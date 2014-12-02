from django.shortcuts import render


""
def error_404(request):
    context = {
        'title': 'Error 404'
    }

    return render(request, 'wui/errors/404.html', context)


""
def error_500(request):
    context = {
        'title': 'Error 500'
    }

    return render(request, 'wui/errors/404.html', context)
