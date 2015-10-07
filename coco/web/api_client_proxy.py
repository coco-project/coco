from coco.client.clients import HttpClient


def get_httpclient_instance(request):
    base_url = "http://localhost/api"
    username = request.user.username
    password = request.session.get('password')
    return HttpClient(base_url, auth=(username, password))


def set_session_password(request):
    if request.POST:
        password = request.POST.get('password')
        request.session['password'] = password
