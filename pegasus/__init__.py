"""PEGASUS: A whiteboard collaboration tool built with Flask

Files:
    The backend is divided into 3 main files, other than the database schema:
        - __init__.py: glues everything together; the configuration, the db connection, 
        the initialization of the app, and the rest of the necessary (sub-)modules.
        - views.py: most of the business logic, aside from error handlers.
        - errorhandlers.py: ...the error handlers.
    The frontend, on the other hand, is divided into 3 main folders, each with several files:
        - templates: all the html/Jinja2 templates.
        - static:
            = css: all the stylesheets
            = js: all the external scripts

Purpose & Functionality:
    General:
        The aim of this project is to create an easy, lightweight, realtime whiteboard to share/demonstrate ideas 
        in the form of components (for example: text, images, code, etc) that can be pieced together and edited
        by several people in a live session, and exported at any time.
        At this point in time, the only component available is text, along with the sidebar chat (which is available to everyone, edit privileges or not).
        The plan is to add components, and features (like exporting the board as text instead of image), gradually, until the project reaches its initial 
        purpose (stated above).

    Use case:
        A user who wishes to create a board registers an account, and proceeds to create it. Once created, they can invite others
        by email either to view the board, or to co-edit it. Invited persons can either directly access the board through their invite
        link, or register using the same email they've been invited with and access the board from their account. 
        The board lasts 24 hours by default, but can be marked as done/expire sooner if the owner marks it as done.
        Once expired, the final form of the board (and the sidebar chat) remain for everyone involved in the board to view or export. 
        Only the owner can delete the board, edit it, and invite people.
        Only signed in, non-owner invited users can remove themselves from the board entirely. 


"""
import sqlite3
from flask import Flask, g, request, session, abort
from contextlib import closing
from flask_jsglue import JSGlue

# config (which should be in another file for larger apps)
DATABASE = '/tmp/pegasus.db'
"""SQLite database file. Schema can be found in schema.sql"""
DEBUG = True
"""For dev purposes."""
SECRET_KEY = 'you shall not pass'
"""Also for dev purposes."""


# initialize app
app = Flask(__name__)
"""Initialize the application."""
jsglue = JSGlue(app)
"""JSGlue is what provides client-side js with Flask's url_for functionality without having to render the links via Jinja2"""
app.config.from_object(__name__) # or the other file if we had the config in another file (ref: app.config.from_envvar('FLASKR_SETTINGS', silent=True))
"""Assign configuration to app. In this case, configuration is in the same file."""

# import other necessary modules
import pegasus.views
import pegasus.errorhandlers

def connect_db():
    """Connect to the SQLite database."""
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    """Initialize the SQLite database. Used in init_db.py."""
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()



# database requests
@app.before_request
def before_request():
    """Before database requests, connect, and turn on foreign keys."""
    g.db = connect_db()
    g.db.execute('PRAGMA foreign_keys = ON')

@app.before_request
def csrf_protect():
    """Before database requests, in case of POST requests, check for the CSRF-protection token in the user's session.
    If present, pop (remove from session and get its value) then compare to the token submitted in the form.
    If there's no token or the token is not equal to the one from the form, abort the request.
    """
    if request.method == 'POST': # GET/ajax protection can be defined in their respective functions
        token = session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(400) 

@app.teardown_request
def teardown_request(exception):
    """If there's a database connection, close it."""
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()



