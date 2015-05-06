import json
import os.path
import requests

# import celery configuration
from ipynbsrv.celery import app


class Docker(object):

    @staticmethod
    @app.task(name='ipynbsrv.wui.tools.commit')
    def commit(host, container, name, tag='latest'):
        url = "http://" + host + ":8080/" + container
        return requests.get(url).content
        #return self.client.commit(container=container, repository=name, tag=tag)

    @staticmethod
    @app.task(name='ipynbsrv.wui.tools.containers')
    def containers(host, quiet=True, all=True):
        # TODO: actually have to get list of containers from every host
        url = "http://" + host + ":8080/container"
        return requests.get(url).content
        #return self.client.containers(quiet=quiet, all=all)

    @staticmethod
    @app.task(name='ipynbsrv.wui.tools.create_container')
    def create_container(host, name, image, cmd, ports=None, volumes=None, env=None, detach=True):
        try:
            return requests.post(
                url="http://%s:8080/containers" % host,
                data=json.dumps({
                    "name": name,
                    "image": image,
                    "command": cmd
                })
            ).content
            print('Response HTTP Status Code : {status_code}'.format(status_code=r.status_code))
            print('Response HTTP Response Body : {content}'.format(content=r.content))
        except:
            print('HTTP Request failed')

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
        return requests.get(url).content
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
        return requests.get(url).content
        #self.client.restart(container=container, timeout=timeout)

    @staticmethod
    @app.task(name='ipynbsrv.wui.tools.start')
    def start(container, host, port_binds=None, volume_binds=None, links=None):
        url = "http://" + host + ":8080/container/" + container + "/start"
        return requests.get(url).content
        #self.client.start(container=container, port_bindings=port_binds, binds=volume_binds, links=links)

    @staticmethod
    @app.task(name='ipynbsrv.wui.tools.stop')
    def stop(host, container, timeout=10):
        url = "http://" + host + ":8080/container/" + container + "/stop"
        return requests.get(url).content
        #self.client.stop(container=container, timeout=timeout)


class Host(object):

    @staticmethod
    @app.task(name='ipynbsrv.wui.tools.host_info')
    def host_info(host):
        url = "http://" + host + ":8080/host/info"
        return requests.get(url).content

    @staticmethod
    @app.task(name='ipynbsrv.wui.tools.host_info')
    def host_status(host):
        url = "http://" + host + ":8080/host/status"
        return requests.get(url).content


    @staticmethod
    @app.task(name='ipynbsrv.wui.tools.service_status')
    def service_status(host, service):
        url = "http://" + host + ":8080/host/service"
        return requests.get(url).content



class Filesystem(object):
    @staticmethod
    def ensure_directory(directory, recursive=False):
        parent = os.path.abspath(os.path.join(directory, os.pardir))
        if recursive and not os.path.exists(parent):
            Filesystem.ensure_directory(parent)
        if not os.path.exists(directory):
            return os.makedirs(directory)
