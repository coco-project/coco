from docker import Client
class Docker:
        def __init__(self):
                self.docker = Client(base_url='tcp://192.168.182.129:9999',version='1.2.1')
        ## Container Commands ##
        def stopContainer(self, id):
                self.docker.stop(container=id)
        def startContainer(self, id):
                self.docker.start(container=id)
        def restartContainer(self, id):
                self.docker.restart(container=id)
        def delContainer(self, id):
                self.docker.remove_container(container=id)
        def createContainer(self, img, cmd, name, tty):
                cont = self.docker.create_container(image=img, command=cmd, tty=tty, name=name)
                return cont
		#container_started.send(sender=self.__class__, cont['Id'])
        def commitContainer(self, id,name,tag):
                self.docker.commit(container=id,repository=name,tag=tag)
        ## Image Commands ##
        def delImage(self, id):
                self.docker.remove_image(image=id)
