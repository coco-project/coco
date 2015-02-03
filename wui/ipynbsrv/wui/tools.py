import os.path
from docker import Client


"""
docker-py wrapper class.
"""
class Docker(object):
    def __init__:
        self.client = Client(base_url='unix://var/run/docker.sock', version=settings.DOCKER_API_VERSION)

    """
    Link: https://github.com/docker/docker-py/blob/master/docs/api.md#containers
    """
    def containers(self, quiet=True, all=True):
        return self.client.containers(quiet=quiet, all=all)

    """
    Link: https://github.com/docker/docker-py/blob/master/docs/api.md#images
    """
    def images(name=None, quiet=True, all=False):
        return self.client.images(name=name, quiet=quiet, all=all)

    """
    Link: https://github.com/docker/docker-py/blob/master/docs/api.md#remove_container
    """
    def remove_container(self, container, force=True):
        self.client.remove_container(container=container, force=force)

    """
    Link: https://github.com/docker/docker-py/blob/master/docs/api.md#remove_image
    """
    def remove_image(self, image, force=True):
        self.client.remove_image(image=image, force=force)

    """
    Link: https://github.com/docker/docker-py/blob/master/docs/api.md#stop
    """
    def stop(self, container, timeout=10):
        self.client.stop(container=container, timeout=timeout)


"""
Utility helper class to work with the filesystem.
"""
class Filesystem(object):
    @staticmethod
    def ensure_directory(directory, recursive=False):
        parent = os.path.abspath(os.path.join(directory, os.pardir))
        if recursive and not os.path.exists(parent):
            Filesystem.ensure_directory(parent)
        if not os.path.exists(directory):
            return os.makedirs(directory)
