Goly
====

Hello, and welcome to Goly!  This is my personal project for creating, monitoring, sharing, and ultimately *achieving* goals.  

The Goly repository contains the code for the Goly API.  Other repositories will contain the code for the Goly front-end(s).

Please note that this project is currently under construction.

API
====
The Goly API accepts and returns JSON data.  Generally, model endpoints are plural (e.g., `/users/` rather than `/user/`).    All canonical endpoints end in a slash (e.g. `/users/` rather than `/users`); failing to specify the slash will result in a redirect, so should still serve the same content, but you may need to specifically follow redirects in your request if you omit the slash.  Multi-word endpoints use dashes, not underscores (e.g. `/users/update-password/` rather than `users/update_password`).  Query parameters use underscores (e.g. `users/index/?sort_order=` rather than `/users/index/?sort-order=`)

Each response will include a `status_code` and a `data` attribute.      

Errors will return an HTTP status code in the 400 range. The response for an error will include a `detail` attribute in the returned data, with information about the error.

OK responses will include a `status_code` in the 200 range.  The resulting `data` attribute will depend on the endpoint in question; each is described below.  Note that array data is always returned as an attribute pointing to an array; this is due to a somewhat obscure security concern detailed [here](http://flask.pocoo.org/docs/0.10/security/#json-security).  Empty return values are provided as empty objects, so it is always safe to JSON decode the `data` attribute of a response.

User API
----
**/register/**  
Methods: POST  
Purpose: Create a new user  
Accepts: 
 - email:  A semantically valid email address; must be unique
 - password: A password for the new user
 - first_name:  The first name of the user
 - last_name: The last name of the user  

Returns:  
- status code: 201
- data: 
  - id: unique integer identifier of the user
  - email: user's email
  - first_name: the created user's first name
  - last_name: the created user's last name
  - registered_on: the UTC time at which the user registered

Errors:
- Status code 400: Invalid request
- Status code 409: Resource already exists, in case of a duplicate email.

**/login/**  
Methods: POST  
Purpose: Log in as an existing user  
Accepts:
 - email:  A semantically valid email address; must exist as a user
 - password: The password of the user
 - remember: Boolean true or false (default); True keeps the user logged in

Returns:
- status code: 201
- data: Empty

Errors:
- Status code 400: Invalid request
- Status code 401: Invalid credentials (see details for more information)

**/logout/**  
Methods: POST  
Purpose: Log out current user  
Accepts:  empty  
Returns:
- status code: 204
- data: empty

Errors: None

**/users/delete/**  
Methods: POST  
Purpose: Delete a user  
Accepts:
 - email:  A semantically valid email address; must be an existing user
 - password: The password of the user to delete

Returns:
- status code: 204
- data: empty

Errors:
- Status code 400: Invalid request
- Status code 401: Invalid credentials (see details for more information)

**/users/update-password/**  
Methods: POST  
Purpose: Update a user's password  
Accepts:
 - email:  A semantically valid email address; must be an existing user
 - old_password: The current password of the user whose password to change
 - new_password: The new password for the user

Returns:
- status code: 200
- data: empty

Errors:
- Status code 400: Invalid request
- Status code 401: Invalid credentials (see details for more information)

**/users/update-email/**  
Methods: POST  
Purpose: Update a user's email address  
Accepts: 
 - old_email:  A semantically valid email address; must be an existing user
 - new_email: A semantically valid email address; must not be an existing user
 - password: The password of the user

Returns:
 - status code: 200
 - data: empty

Errors:
- Status code 400: Invalid request
- Status code 401: Invalid credentials (see details for more information)
 - Status code 409: Resource already exists, in case of a duplicate new email.

**/users/update/**  
Methods: POST  
Purpose: Update a user's non-email or password fields  
Accepts:
 - email:  A semantically valid email address; must be an existing user
 - password: The password of the user to update
 - first_name: Optional, a new first name for the user
 - last_name: Optional, a new last name for the user

Returns:
 - status code: 200
 - data: empty

Errors:
- Status code 400: Invalid request
- Status code 401: Invalid credentials (see details for more information)

**/users/me/**  
Methods: GET  
Purpose: Get the current user's information  
Requires login  
Returns:
 - status code: 200
 - data: same as returned by /users/[id]/

Errors:
- Status code 401: You must login

**/users/[id]/**  
Methods: GET  
Purpose: Get the specified user's information  
Requires login  
Returns:
- status code: 200
- data:
  - id: unique integer identifier of the user
  - email: user's email
  - first_name: the user's first name
  - last_name: the user's last name
  - registered_on: the UTC time at which the user registered

Errors:
- Status code 401: You must login
- Status code 404: Not found

**/users/[id]/**  
Methods: GET  
Purpose: Get the specified user's information  
Requires login  
Returns:
- status code: 200
- data:
  - id: unique integer identifier of the user
  - email: user's email
  - first_name: the user's first name
  - last_name: the user's last name
  - registered_on: the UTC time at which the user registered

Errors:
- Status code 401: You must login
- Status code 404: Not found

**/users/index/**  
Methods: GET  
Purpose: Get a list of users' information  
Requires login  
Parameters:
- count: numeric, the number of entries to receive; default 20
- offset: numeric, the number of entries to skip; default 0
- sort: a field to sort by, must be one of 'id', 'email', 'first\_name', 'last\_name', 'registered_on'; default is 'email'
- sort_order: "asc" or "desc", default "asc"

Returns:
- status code: 200
- data:
  - users: an array of length no greater than _count_ with user objects as returned by /users/[id]/

Errors:
- Status code 400: Invalid request
- Status code 401: You must login
 
Goal API
----
**/goals/create/**  
Methods: POST  
Purpose: Create a new goal for the current user
Requires login  
Accepts:
- name: A (short) name to display for the goal, e.g., "Friend Call"
- prompt: A prompt (question) to answer, e.g., "Did you call a friend today?"
- frequency: The frequency with which this task should be performed -- one of "daily", "weekly", "monthly", "quarterly", or "yearly"
- target: The target number of times within the frequency range to perform the task (e.g., 1 [friend call per day] or 5 [workouts per week]) 
- input_type: Either "numeric" or "binary."  
  - Numeric: Enter a number to indicate the number of times you performed the task (e.g., if your goal is to practice guitar 180 minutes / week, your prompt might be "How many minutes of guitar did you practice today?" and your answer might be 45.
  - Binary: A yes / no action.  (e.g., if your goal is to call a friend every day, your prompt might be "Did you call a friend today" and your answer might be "Yes.")
- check_in_frequency: The frequency with which to check in on the goal (i.e., receive push notifications).  Check-in frequency must be one of the options for frequency, and likewise must be conformant (i.e., if "frequency" is "monthly", check-in frequency must be daily, not weekly (since weeks and months don't divide evenly) or yearly (since years are shorter than months))

Returns:  
- status code: 201
- data: 
  - id: The ID of the newly created goal
  - user: The ID of the user who created the goal 
  - name: The name of the goal
  - prompt: The goal's prompt
  - frequency: The goal's frequency
  - check_in_frequency: The frequency with which to check-in on this goal; this is also the unit provided in detail reports
  - target: The numerical target of the goal
  - input_type: The input type of the goal
  - active: Whether the goal is currently active (Default: true)
  - public: Whether the goal is currently publicly viewable (Default: false)
  - created: The time at which the goal was created

Errors:
- Status code 400: Invalid request
- Status code 401: You must login
- Status code 409: Resource already exists, in case of a duplicate name

**/goals/delete/**  
Methods: POST  
Purpose: Delete a goal for the current user
Requires login  
Accepts:
- id: The ID of the goal to delete

Returns:  
- status code: 204
- data: empty

Errors:
- Status code 400: Invalid request
- Status code 401: You must login
- Status code 401: Invalid Credentials (trying to delete a goal that is not the current user's)
- Status code 409: Resource already exists, in case of a duplicate name

**/goals/update/**  
Methods: POST  
Purpose: Update an existing goal for the current user
Requires login  
Accepts:
- id: Required, the ID of the goal to update
- name (optional): A new (short) name to display for the goal, e.g., "Friend Call". Must be unique.
- prompt (optional): A new prompt (question) to answer, e.g., "Did you call a friend today?"
- frequency (optional): The new frequency with which this task should be performed -- one of "daily", "weekly", "monthly", "quarerly", or "yearly"
- check_in_frequency (otpional): The new frequency with which to check in on this task; same options as "frequency"
- target (optional): The new target number of times within the frequency range to perform the task (e.g., 1 [friend call per day] or 5 [workouts per week]) 
- input_type (optional): Either "numeric" or "binary."  
  - Numeric: Enter a number to indicate the number of times you performed the task (e.g., if your goal is to practice guitar 180 minutes / week, your prompt might be "How many minutes of guitar did you practice today?" and your answer might be 45.
  - Binary: A yes / no action.  (e.g., if your goal is to call a friend every day, your prompt might be "Did you call a friend today" and your answer might be "Yes.")
- active (optional): True / False, whether the goal should be considered "active" (i.e., prompted for nightly)
- public (optional): True / False, whether the goal and its progress should be displayed publicly to other users

Returns:  
- status code: 200
- data: empty

Errors:
- Status code 400: Invalid request
- Status code 401: You must login
- Status code 401: Invalid Credentials (attempting to update another user's goal)
- Status code 404: Specified goal does not exist
- Status code 409: Resource already exists, in case of a duplicate name
  
**/goals/[id]/**  
Methods: GET  
Purpose: Get information about a single goal
Requires login  

Returns:
- status code: 200
- data:
  - A single goal, as returned by the /goals/create/ endpoint.

Errors:
- Status code 400: Invalid request
- Status code 401: You must login
- Status code 401: Invalid Credentials (attempting to access another user's private goal)
- Status code 404: Not Found (specified goal does not exist)

**/goals/users/[id]/**  
Methods: GET  
Purpose: Get a user's public goals
Requires login  
Parameters:
- count: numeric, the number of entries to receive; default 20
- offset: numeric, the number of entries to skip; default 0
- sort: a field to sort by, must be one of 'id', 'created', 'name', 'frequency'; default is 'name'.  Return is always sorted with active goals first
- sort_order: "asc" or "desc", default "asc"
Returns:
- status code: 200
- data:
  - goals: An array of goals as returned by /goals/[id]/

Errors:
- Status code 400: Invalid request
- Status code 401: You must login
- Status code 404: Not Found (specified user ID does not exist)

**/goals/users/me/**  
Methods: GET  
Purpose: Get current user's public and private goals
Requires login  
Parameters:
- count: numeric, the number of entries to receive; default 20
- offset: numeric, the number of entries to skip; default 0
- sort: a field to sort by, must be one of 'id', 'created', 'name', 'frequency'; default is 'name'.  Return is always sorted with active goals first
- sort_order: "asc" or "desc", default "asc"
Returns:
- status code: 200
- data:
  - goals: An array of goals as returned by /goals/[id]/

Errors:
- Status code 400: Invalid request
- Status code 401: You must login
 
Check-in API
----
**/goals/[id]/check-ins/**  
Methods: POST  
Purpose: Create a new check-in or update an existing one
Requires login  
Accepts:
- value: The value of the check-in.  For numeric goals, this must be numeric; likewise, for binary goals, this must be one of "True" or "False"
- timeframe: Optional; the ID of a timeframe whose check-in to update or create; if not specified, assumes the current timeframe.

Returns:
- status code: 201 if the check-in is created or 200 if an existing check-in is updated
- data:
  - id: The id of the newly-created or updated check-in
  - goal: The id of the goal
  - timeframe: A representation of the timeframe, with fields
    - id: the id of the timeframe
    - frequency: The frequency of the timeframe; should match check-in frequency
    - Start: The start of the timeframe for which this check-in applies, in format YYYY-MM-DD HH:mm:ss (e.g., 2016-01-01 00:00:00)
    - End: The end of the timeframe for which this check-in applies, in format YYYY-MM-DD HH:mm:ss (e.g., 2016-01-01 00:00:00); timeframe does *not* include its end.
  - value: The value of the check-in.  Always numeric, even if the goal is binary, in which case True is converted to 1 and False to 0.

Errors:
- Status code 400: Invalid request; see message
- Status code 401: You must login or you do not own the goal in question
- Status code 404: The specified goal does not exist

**/goals/[id]/check-ins/current/**  
Methods: GET
Purpose: Get the check-in for a given goal for the current timeframe
Requires login  
Parameters: None

Returns:
- status code: 200 if the check-in exists
- data:
  - id: The id of the current check-in
  - goal: The id of the goal
  - timeframe: A representation of the timeframe, with fields
    - id: the id of the timeframe
    - frequency: The frequency of the timeframe; should match check-in frequency
    - Start: The start of the timeframe for which this check-in applies, in format YYYY-MM-DD HH:mm:ss (e.g., 2016-01-01 00:00:00)
    - End: The end of the timeframe for which this check-in applies, in format YYYY-MM-DD HH:mm:ss (e.g., 2016-01-01 00:00:00); timeframe does *not* include its end.
  - value: The value of the check-in.  Always numeric, even if the goal is binary, in which case True is converted to 1 and False to 0.

Errors:
- Status code 400: Invalid request; see message
- Status code 401: You must login or you do not own the goal in question
- Status code 404: The specified goal or check-in does not exist

**/goals/[id]/check-ins/[tfid]/**  
Methods: GET
Purpose: Get the check-in value for a given goal and timeframe
Requires login  
Parameters: None

Returns:
- status code: 200 if the check-in exists
- data:
  - id: The id of the current check-in
  - goal: The id of the goal
  - timeframe: A representation of the timeframe, with fields
    - id: the id of the timeframe
    - frequency: The frequency of the timeframe; should match check-in frequency
    - Start: The start of the timeframe for which this check-in applies, in format YYYY-MM-DD HH:mm:ss (e.g., 2016-01-01 00:00:00)
    - End: The end of the timeframe for which this check-in applies, in format YYYY-MM-DD HH:mm:ss (e.g., 2016-01-01 00:00:00); timeframe does *not* include its end.
  - value: The value of the check-in.  Always numeric, even if the goal is binary, in which case True is converted to 1 and False to 0.

Errors:
- Status code 400: Invalid request; see message
- Status code 401: You must login or you do not own the goal in question
- Status code 404: The specified goal or check-in does not exist

**/goals/[id]/check-ins/**  
Methods: GET
Purpose: Get an index of check-ins within a  given time window
Requires login  
Parameters: 
- start: The start of the time window, in format YYYY-MM-DD hh:mm:ss (2016-01-01 00:00:00, e.g.)
- end: The end of the time window, in format YYYY-MM-DD hh:mm:ss (2016-01-01 00:00:00, e.g.)

Returns:
- status code: 200
- data:
  - check-ins: an array of check-ins in format returned from /goals/[id]/check-ins/current/
  
Errors:
- Status code 400: Invalid request; see message
- Status code 401: You must login or you do not own the goal in question
- Status code 404: The specified goal does not exist
 
Installation
====
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
====
* Build front-end!
