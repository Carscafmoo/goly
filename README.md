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
The developers of this project use MySQL, and the requirements.txt ships with python-mysql included. However, you could technically use any SQLAlchemy-supported system, but you may need to install the relevant packages yourself.  To use the MySQL storage that the project ships with, you will need a functional deployment of MySQL. 

Migrations are effected using [alembic](https://alembic.readthedocs.org/en/latest/).

Configuration
----
Goly expects a file called `goly.cfg` at the `[app]/goly` level.  This file must contain the information provided in the following example:
```
SQLALCHEMY_DATABASE_URI='mysql://user:password@host/db'
SQLALCHEMY_ECHO = False
SECRET_KEY = 'your secret key here'
#DEBUG = True # comment out for deployment obviously
```
For alembic's migrations to work, Goly also expects an `alembic.ini` file at the `[app]/` level.  See [Alembic's documentation on editing the alembic.ini](https://alembic.readthedocs.org/en/latest/tutorial.html#editing-the-ini-file) file for more information on what that file should look like.

Todos
----
* Pretty much everything!
