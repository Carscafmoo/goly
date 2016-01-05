Goly
====

Hello, and welcome to Goly!  This is my personal project for creating, monitoring, sharing, and ultimately *achieving* goals.  

Please note that this project is currently under construction. 

Installation
----
The Goly back-end is a Python Flask application.  To install, you'll need Python 2.7 (I use 2.7.10).  Instructions for installing Python 2.7 can be found on the [Python website](https://www.python.org/).  

I also recommend using a virtual environment for dependency management.  Python comes with a nifty one called [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/).  You can follow the directions to install and use virtualenv, but the long and short of it is pretty simple:
```
> pip install virtualenv
> cd [your directory]
> virtualenv .
> . venv/bin/activate
```
When activated, you can run all of your dependency installations.  We create a file called `requirements.txt` to help manage this:
```
> pip install -r requirements.txt
```
Then, to deactivate your virtual environment, simply run
```
> deactivate
```

### Storage layer
Our storage layer is MySQL -- you will need a functional deployment of MySQL on your back-end server. 