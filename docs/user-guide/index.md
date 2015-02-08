# User-Guide

## Create an Ipython-Notebook-Container, install Ipython Modules and share the Container
Creating an Ipython-Notebook-Container is a pretty easy task. All you have to do is clicking on the "Create Container"-Button, chose the image you want to create from, chose a name and if you want, you can write a description for it.

To install Ipython-Modules you have simply to connect via SSH-Client to the Container and install the module you want. The SSH-Port from a running Container is shown in the description from the Container.

	pip3 install "Module-Name"

Now you want to share your Container as an image, from which other users can create a Container. To do that, you have to click on the button "share" in the context menu of the container. In the upcoming window, you can specify the name of the image you are creating.

## Create an Ipython-Notebook and share it afterwards 

First you have to connect to the running Container. When you are connected, you can see the usual Ipython-Notebook Page. There you can change the directory you are working in. If you want to create a private Notebook you have to go into your home-folder and press on "create"-Button.

If you created a private Notebook in your home-folder and now you want to share this Notebook, you have to connect via SSH-Client to the Container, where the Notebook is saved. Then you have to manually copy the Notebook into the Share you want. Last but not least you have to change the permissions, so everyone in the Share has Access to it. 
	
	cp /data/home/"Ipython-Notebook" /data/shares/"Share-Name"/

	chmod 660 "Ipython-Notebook"

