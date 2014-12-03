from docker import Client
from ipynbsrv.wui.models import Host, Tag, Container, User, Group, Image, Share
class Database:
        def __init__(self):
                self.docker = Client(base_url='tcp://127.0.0.1:9999',version='1.2.1')
            ## Container Commands ##
        def stopContainer(self, id):
                c = getContainer(id)
                c.status = False
                c.save()
                self.docker.stop(container=id)
        def startContainer(self, id):
                c = getContainer(id)
                c.status = True
                c.save()
                self.docker.start(container=id)
        def restartContainer(self, id):
                self.docker.restart(container=id)
        def getContainerByStatus(stat):
                c = Container.objects.all().filter(status=stat)
                return c
        def getContainer(id):
                c = Container.objects.all().filter(ct_id=id)
                return c
        def delContainer(self, id):
                c = getContainer(id)
                c.delete()
                self.docker.remove_container(container=id)
        def createContainer(self, img, cmd, name, tty, description, host, ownerId):
                cont = docker.create_container(image=img, command=cmd, tty=tty, name=name)
                c = Container(ct_id=cont['Id'], name=name, description=description, status=True, host=host, image=img, owner=getUserId(ownerId))
                startContainer(self, cont['Id'])
        def commitContainer(self, id,name,tag):
                self.docker.commit(container=id,repository=name,tag=tag)
        ## Image Commands ##
        def getImage(id):
                i = Image.objects.all().filter(img_id=id)
                return i.get(pk=1)
        def delImage(self, id):
                self.docker.remove_image(image=id)
        ## Simple Getters & Setters ##
        def getUserId(name):
                u = User.objects.all().filter(username=name)
                return u.get(pk=1).uid
        def getGroupId(name):
                g = Group.objects.all().filter(groupname=name)
                return g.get(pk=1).gid
        def createHost(ip,fqdn,username,ssh_port,ssh_pub_key,ssh_priv_key,docker_version,docker_port):
                h = Host(ip=ip,fqdn=fqdn,username=username,ssh_port=ssh_port,ssh_pub_key=ssh_pub_key,ssh_priv_key=ssh_priv_key,docker_version=docker_version,docker_port=docker_port)
                h.save()
        def getHost(ip):
                h = Host.objects.all().filter(ip=ip)
                return h.get(pk=1)
        def createTag(lab):
                t = Tag(label=lab)
                t.save()
        def getTags():
                return Tag.objects.al()
        def createShare(name, description, owner, group, tags):
                s = Share(name=name, description=description, owner=getUserId(owner), group=getGroupId(group), tags)
                s.save()
        def getShares():
                return Share.objects.all()
                
