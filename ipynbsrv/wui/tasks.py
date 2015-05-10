import os.path
from ipynbsrv.backends.container_backends import *

# import celery configuration
from ipynbsrv.celery import app


class ContainerTask(object):
    '''
    This class holds all the tasks needed to call the host API of a docker host
    to manage its containers.
    The methods take a container_backend instance as a parameter, that holds
    the IP and Port of the target host API, as well as all the API call logic.
    '''

    default_port = '8080'

    @staticmethod
    @app.task(name='ipynbsrv.wui.tasks.commit')
    def commit(container_backend, container, name, tag='latest'):
        return container_backend.commit()

    @staticmethod
    @app.task(name='ipynbsrv.wui.tasks.containers')
    def containers(container_backend, quiet=True, all=True):
        # TODO: actually have to get list of containers from every host
        return container_backend.get_containers()

    @staticmethod
    @app.task(name='ipynbsrv.wui.tasks.create_container')
    def create_container(container_backend, name, image, cmd, ports=None, volumes=None, env=None, detach=True):

        r = container_backend.create_container({
            "name": name,
            "image": image,
            "command": cmd
        })
        print('Response HTTP Status Code : {status_code}'.format(status_code=r.status_code))
        print('Response HTTP Response Body : {content}'.format(content=r.content))
        return r.content

    @staticmethod
    @app.task(name='ipynbsrv.wui.tasks.remove_container')
    def remove_container(container_backend, container, force=True):
        return container_backend.delete(container)

    @staticmethod
    @app.task(name='ipynbsrv.wui.tasks.images')
    def images(container_backend,  name=None, quiet=True, all=False):
        return container_backend.get_images()

    @staticmethod
    @app.task(name='ipynbsrv.wui.tasks.remove_image')
    def remove_image(container_backend, image, force=True):
        return container_backend.remove_image(image)

    @staticmethod
    @app.task(name='ipynbsrv.wui.tasks.restart')
    def restart(container_backend, container, timeout=10):
        return container_backend.restart_container(container)

    @staticmethod
    @app.task(name='ipynbsrv.wui.tasks.start')
    def start(container_backend, container, port_binds=None, volume_binds=None, links=None):
        # TODO: port bindings, volume bindings, links
        return container_backend.start_container(container)        

    @staticmethod
    @app.task(name='ipynbsrv.wui.tasks.stop')
    def stop(container_backend, container, timeout=10):
        return container_backend.stop_container(container)


class HostTask(object):
    '''
    TODO:
    - extend container backend for host information requests
    - adjust this class to use the container_backend for API calls
    '''

    @staticmethod
    @app.task(name='ipynbsrv.wui.tasks.host_info')
    def host_info(hostname_or_ip, port='8080'):
        url = "http://{0}:{1}/host/info".format(hostname_or_ip, port)
        return requests.get(url).content

    @staticmethod
    @app.task(name='ipynbsrv.wui.tasks.host_info')
    def host_status(hostname_or_ip, port='8080'):
        url = "http://{0}:{1}/host/status".format(hostname_or_ip, port)
        return requests.get(url).content

    @staticmethod
    @app.task(name='ipynbsrv.wui.tasks.service_status')
    def service_status(hostname_or_ip, service,  port='8080',):
        url = "http://{0}:{1}/host/service{2}".format(hostname_or_ip, port, service)
        return requests.get(url).content


class Filesystem(object):
    '''
    TODO: document
    '''

    @staticmethod
    def ensure_directory(directory, recursive=False):
        parent = os.path.abspath(os.path.join(directory, os.pardir))
        if recursive and not os.path.exists(parent):
            Filesystem.ensure_directory(parent)
        if not os.path.exists(directory):
            return os.makedirs(directory)
