import os.path

from requests import request

# import celery configuration
from ipynbsrv.celery import app


class Docker(object):

    @staticmethod
    @app.task(name='ipynbsrv.wui.tools.commit')
    def commit(host, container, name, tag='latest'):
        url = "http://" + host + ":8080/" + container
        return request('get', url).content
        #return self.client.commit(container=container, repository=name, tag=tag)

    @staticmethod
    @app.task(name='ipynbsrv.wui.tools.containers')
    def containers(host, quiet=True, all=True):
        # TODO: actually have to get list of containers from every host
        url = "http://" + host + ":8080/container"
        return request('get', url).content
        #return self.client.containers(quiet=quiet, all=all)

    @staticmethod
    @app.task(name='ipynbsrv.wui.tools.create_container')
    def create_container(host, name, image, cmd, ports=None, volumes=None, env=None, detach=True):
        # TODO: build request, choose host
        return str("[POST] http://" + host + ":8080/container")
        return self.client.create_container(name=name, image=image, command=cmd, ports=ports,
                                            volumes=volumes, environment=env, detach=detach)

    @staticmethod
    @app.task(name='ipynbsrv.wui.tools.remove_container')
    def remove_container(host, container, force=True):
        # TODO: build request
        # TODO: does host have to be provided? otherwise search for host
        return str("[DELETE] http://" + host + ":8080/container/" + container)
        #self.client.remove_container(container=container, force=force)

    @staticmethod
    @app.task(name='ipynbsrv.wui.tools.images')
    def images(host, name=None, quiet=True, all=False):
        url = "http://" + host + ":8080/images"
        return request('get', url).content
        #return self.client.images(name=name, quiet=quiet, all=all)

    @staticmethod
    @app.task(name='ipynbsrv.wui.tools.remove_image')
    def remove_image(host, image, force=True):
        url = "http://" + host + ":8080/images/" + image
        # TODO: check url
        return request('delete', url).content
        #self.client.remove_image(image=image, force=force)

    @staticmethod
    @app.task(name='ipynbsrv.wui.tools.restart')
    def restart(host, container, timeout=10):
        url = "http://" + host + ":8080/container/" + container + "/restart"
        return request('get', url).content
        #self.client.restart(container=container, timeout=timeout)

    @staticmethod
    @app.task(name='ipynbsrv.wui.tools.start')
    def start(container, host, port_binds=None, volume_binds=None, links=None):
        url = "http://" + host + ":8080/container/" + container + "/start"
        return request('get', url).content
        #self.client.start(container=container, port_bindings=port_binds, binds=volume_binds, links=links)

    @staticmethod
    @app.task(name='ipynbsrv.wui.tools.stop')
    def stop(host, container, timeout=10):
        url = "http://" + host + ":8080/container/" + container + "/stop"
        return request('get', url).content
        #self.client.stop(container=container, timeout=timeout)


class Filesystem(object):
    @staticmethod
    def ensure_directory(directory, recursive=False):
        parent = os.path.abspath(os.path.join(directory, os.pardir))
        if recursive and not os.path.exists(parent):
            Filesystem.ensure_directory(parent)
        if not os.path.exists(directory):
            return os.makedirs(directory)
