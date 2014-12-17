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
        self.docker.start(container=id, port_bindings={8888: None}, links=[('ipynbsrv.ldap','ipynbsrv.ldap')], binds={'/srv/ipynbsrv/homes/mk':{'bind':'/home/mk'},'/srv/ipynbsrv/public':{'bind':'/data/public'},'/srv/ipynbsrv/shares':{'bind':'/data/shares'}})

    def restartContainer(self, id):
        self.docker.restart(container=id)

    def delContainer(self, id):
        self.docker.remove_container(container=id)

    def createContainer(self, img, name, tty):
        cont = self.docker.create_container(image=img.img_id, tty=tty, name=name, ports=[80], command=img.cmd, volumes=['/srv/ipynbsrv/homes','/srv/ipynbsrv/public','/srv/ipynbsrv/shares'])
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
