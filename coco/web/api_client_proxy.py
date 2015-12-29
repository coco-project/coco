from coco.client.clients import HttpClient
from django.core.urlresolvers import reverse


def get_httpclient_instance(request):
    # TODO: make this url dynamic
    base_url = 'http://localhost{}'.format(reverse('api_root'))
    username = request.user.username
    password = request.session.get('password')
    return HttpClient(base_url, auth=(username, password))


def set_session_password(request):
    if request.POST:
        password = request.POST.get('password')
        request.session['password'] = password
