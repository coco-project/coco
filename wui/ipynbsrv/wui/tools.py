import os.path
from docker import Client


"""
"""
class Docker(object):
    def __init__(self):
        self.docker = Client(base_url='unix://var/run/docker.sock',version='1.12')

    ## Container Commands ##
    def stopContainer(self, id):
        self.docker.stop(container=id)

    def startContainer(self, id):
        self.docker.start(container=id, port_bindings={8888: None})

    def restartContainer(self, id):
        self.docker.restart(container=id)

    def delContainer(self, id):
        self.docker.remove_container(container=id)

    def createContainer(self, img, cmd, name, tty):
        cont = self.docker.create_container(image=img, command=cmd, tty=tty, name=name, ports=[80])
        return cont

    def commitContainer(self, id,name,tag):
        self.docker.commit(container=id,repository=name,tag=tag)

    def containers(self):
	return self.docker.containers()

    def containersall(self):
	return self.docker.containers(all=True)

    ## Image Commands ##
    def images(self):
        img = self.docker.images(all=True, quiet=False)
        return img

    def images_name(self, name):
        img = self.docker.images(name=name, all=True, quiet=False)
        return img

    def delImage(self, id):
        self.docker.remove_image(image=id)


"""
"""
class Filesystem(object):
    """
    Helper class to work with the filesystem.
    """
    @staticmethod
    def ensure_directory(directory, recursive=False):
        parent = os.path.abspath(os.path.join(directory, os.pardir))
        if recursive and not os.path.exists(parent):
            Filesystem.ensure_directory(parent)
        if not os.path.exists(directory):
            return os.makedirs(directory)
