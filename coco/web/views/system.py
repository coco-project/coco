from django.shortcuts import render


def error_404(request):
    '''
    Error 404 - Page Not Found error view.
    '''
    return render(request, 'web/errors/404.html', {
        'title': "Error 404"
    })


def error_500(request):
    '''
    Error 500 - Internal Server Error view.
    '''
    return render(request, 'web/errors/500.html', {
        'title': "Error 500"
    })
