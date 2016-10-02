.. Pegasus documentation master file, created by
   sphinx-quickstart on Sat May  7 11:17:20 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Pegasus
=======

.. toctree::
   :maxdepth: 2

.. _intro:

Introduction
-------------
About
~~~~~~
Pegasus is a whiteboard collaboration app whose aim is to enable/facilitate realtime sharing of ideas in the form of components (for example: text, images, code, etc) that can be pieced together and edited by several people in a live session, and exported at any time.

At this point in time (*v0.1.0*), the only component available is text, along with the sidebar chat (which is available to everyone, edit privileges or not).

The plan is to add components, and features (like exporting the board as text instead of image), gradually, until the project reaches its initial purpose (stated above).

This project was part of the second edition of `Learn IT, Girl`_, and would not have been possible without the continuous mentorship, support, and tolerance of 'newbie' questions courtesy of `@daniel-j-h`_. 

Rules
~~~~~~
- Signed up users can create a board, to which they can give any number of other users access.
- Each board can have 3 types of users with access:
	- **Owner**
		Can do everything others can plus: edit board title, terminate board early, invite others and control their permissions, and delete the board.
	- **Editor**
		Can do everything viewers can plus: edit the components of the board.
	- **Viewer**
		Can only view the board, export its content at any time, and participate in the sidebar chat.
- **Editors** and **Viewers** can access the board either by signing into the website using the email they were invited with or accessing it through their unique invite link.
- Any signed in user with access to a certain board who is also not its **Owner** can remove themselves at any time.
- To avoid editing conflict, only one person can edit the board at a time.

.. note:: In order to simplify interaction with the server, most of the "heavy lifting" is done client-side. The server simply records and supplies data about the board as needed, and the client pieces it together in the DOM. The client-side board logic can be found `on Github`_.

Installation
~~~~~~~~~~~~
1. Clone the repo. 
::
	$ git clone https://github.com/blaringsilence/pegasus.git
	$ cd pegasus
2. Install `virtualenv`_ and activate it.
::
	$ pip install virtualenv
	$ virtualenv venv
	$ . venv/bin/activate
	$ pip install -r requirements.txt
3. Initialize the database.
::
	$ chmod a+x init_db.py
	$ ./init_db.py
4. Run the app.
::
	$ chmod a+x run_pegasus.py
	$ ./run_pegasus.py
.. note:: Default IP:port is 127.0.0.1:5000. You can change that by specifying the port and/or IP like this:
	``$ ./run_pegasus.py -ip IP_ADDRESS -port PORT_NUMBER``


.. _Learn IT, Girl: http://learnitgirl.com
.. _@daniel-j-h: https://github.com/daniel-j-h
.. _virtualenv: https://pypi.python.org/pypi/virtualenv
.. _on Github: https://github.com/blaringsilence/pegasus/blob/master/pegasus/templates/show-board.html

.. _docs:

Docs
-----
.. automodule:: pegasus
	:members:
	:exclude-members: Flask, pegasus, views, errorhandlers, DATABASE, DEBUG, SECRET_KEY, app

.. automodule:: pegasus.views
	:members:

.. automodule:: pegasus.errorhandlers
	:members:

.. automodule:: test_pegasus
	:members:

