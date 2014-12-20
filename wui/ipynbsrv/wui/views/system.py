from django.shortcuts import render


"""
Error 404 - Page not found error view.
"""
def error_404(request):
    return render(request, 'wui/errors/404.html', context = {
        'title': "Error 404"
    })


"""
Error 500 - Internal Server Error view.
"""
def error_500(request):
    return render(request, 'wui/errors/500.html', context = {
        'title': "Error 500"
    })
