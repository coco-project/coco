from ipynbsrv.client.clients import HttpClient


def get_httpclient_instance(request):
    base_url = "http://localhost:8000/api"
    username = request.user.username
    password = request.session.get('password')
    print("{}:{}".format(username, password))
    return HttpClient(base_url, auth=(username, password))


def set_session_password(request):
    if request.POST:
        password = request.POST.get('password')
        request.session['password'] = password
