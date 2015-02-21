
# User-Guide

## What is the purpose of this website?

This website offers a management point for multiple instances of IPython Notebooks. 

First of all you need to know some Words:

 - IPython Notebook 

The IPython Notebook is a Python IDE in the Browser. It allows to work on documents, which can contain formatted text, runnable Code, such as graphical Output. In this User-Guide we are not covering how to use an IPython Notebook. If you need help in this topic, you have to go their [Website](http://ipython.org/notebook.html).

 - Container

One instance of IPython Notebook runs in one Container. It serves as Software Stack for this instance. You can share and manage the Container in the Container register. More information about these topics are written below.

 - Image

An Image provides a backup of a Software Stack. You can use them to save a Software Stack for yourself or to provide it to other Users.



## Create a Container

Creating an IPython-Notebook-Container is an easy task. On the Container register you have to click on the *Create Container*-Button.  This opens a form, where you can specify the name of the Container, give it a description and chose the base image from where it creates the Container. 


## Manage my Container

In the context menu of every Container, you can manage it with different commands. You can for example start, stop, share the Container or connect to the IPython Notebook running in it. 

If you want to move some Notebooks or if you want to change the permissions of it, you have to connect to the Container via SSH-Client like *Putty*. The SSH-Port of a running Container is written in the description of the Container in the Container register.


## Where can i store my data?
There are three different locations where you can have your data:

*	/home

Here you can save your personal Notebooks. You have access to it in every Container.

*	/data/shares

For every share you are permitted to access, you have a folder in you shares directory. Every other user in this share can see the Notebooks in it.

*	/data/public

If you want to make your Notebook available for the public, you can export it as HTML-File and put it in your public folder.

## I want to install Modules!

From the description of a running Container you can get the SSH-Port the machine is listening to. You can connect with a shell-program like *Putty* to it. There you have to log in with your user credentials and type in following command to install the desired modules:
```python
pip3 install "Module-Name"
```


## Share my Software Stack (Container)

After you installed some Modules you maybe want to share your Container as a Software Stack, so other Users can use it as a base for their Containers. You can simply do that by creating an image from the Container, where you installed the modules. You can do this step with two different ways:

*	Click on "Share" in the context menu of the specified Container on the Container register. 
*	Create an image on the Image register and chose the Container, where you installed the modules. 

Either way it opens a window where you have to chose a concise name, so other users will know what the image offers. If you just want to offer you a backup of your software stack you can do this by unchecking the *"public"*-checkbox.



## Share my IPython Notebooks

If you created a private Notebook in your home-folder and now you want to share this Notebook, you have to connect via SSH-Client to the Container, where the Notebook is saved. Then you have to manually copy the Notebook into the Share you want. Last but not least you have to change the permissions, so everyone in the Share has Access to it. 

```python
cp /data/home/"IPython-Notebook" /data/shares/"Share-Name"/

chmod 660 "IPython-Notebook"
```
