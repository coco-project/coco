import os.path
from django.conf import settings
from docker import Client


class Docker(object):
    def __init__(self):
        self.client = Client(base_url='unix://var/run/docker.sock', version=settings.DOCKER_API_VERSION)

    def commit(self, container, name, tag='latest'):
        return self.client.commit(container=container, repository=name, tag=tag)

    def containers(self, quiet=True, all=True):
        return self.client.containers(quiet=quiet, all=all)

    def create_container(self, name, image, cmd, ports=None, volumes=None, env=None, detach=True):
        return self.client.create_container(name=name, image=image, command=cmd, ports=ports,
                                            volumes=volumes, environment=env, detach=detach)

    def images(self, name=None, quiet=True, all=False):
        return self.client.images(name=name, quiet=quiet, all=all)

    def remove_container(self, container, force=True):
        self.client.remove_container(container=container, force=force)

    def remove_image(self, image, force=True):
        self.client.remove_image(image=image, force=force)

    def stop(self, container, timeout=10):
        self.client.stop(container=container, timeout=timeout)


class Filesystem(object):
    @staticmethod
    def ensure_directory(directory, recursive=False):
        parent = os.path.abspath(os.path.join(directory, os.pardir))
        if recursive and not os.path.exists(parent):
            Filesystem.ensure_directory(parent)
        if not os.path.exists(directory):
            return os.makedirs(directory)
