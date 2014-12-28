import os.path
from docker import Client


class Docker(object):
    def __init__(self):
        self.docker = Client(base_url='unix://var/run/docker.sock',version='1.12')

    ## Container Commands ##
    def stopContainer(self, id):
        self.docker.stop(container=id)

    def startContainer(self, id, ports, exposeport, user):
	portd = {}
	portl = ports.split(',')
	string1 = "/srv/ipynbsrv/homes/{{USER}}"
	string2 = "/home/{{USER}}"
	string1 = string1.replace("{{USER}}", user)
	string2 = string2.replace("{{USER}}", user)
        bs={string1:{'bind':string2},'/srv/ipynbsrv/public':{'bind':'/data/public'},'/srv/ipynbsrv/shares':{'bind':'/data/shares'}}
	for port in portl:
		port = port.strip()
		if port == "8888":
		    portd[8888] = exposeport
		else:
		    portd[port] = 'None'
        self.docker.start(container=id, port_bindings=portd, links=[('ipynbsrv.ldap','ipynbsrv.ldap')], binds=bs)

    def restartContainer(self, id):
        self.docker.restart(container=id)

    def delContainer(self, id):
        self.docker.remove_container(container=id)

    def createContainer(self, img, name, tty, ports, exposeport):
	port = ports.split(',')
	ps = []
	cmd = img.cmd.replace("{{port}}", str(exposeport))
	for p in port:
		ps.append(p.strip())
        cont = self.docker.create_container(image=img.img_id, tty=tty, name=name, ports=ps, command=cmd, volumes=['/srv/ipynbsrv/homes','/srv/ipynbsrv/public','/srv/ipynbsrv/shares'])
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
