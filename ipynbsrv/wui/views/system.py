from django.shortcuts import render


def error_404(request):
    """
    Error 404 - Page not found error view.
    """
    return render(request, 'wui/errors/404.html', {
        'title': "Error 404"
    })


def error_500(request):
    """
    Error 500 - Internal Server Error view.
    """
    return render(request, 'wui/errors/500.html', {
        'title': "Error 500"
    })
