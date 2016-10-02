"""
App
----
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
CSRF_ENABLED = True
"""To be able to disable it when testing"""


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
    if request.method == 'POST' and app.config['CSRF_ENABLED']: # GET/ajax protection can be defined in their respective functions
        token = session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(400) 

@app.teardown_request
def teardown_request(exception):
    """If there's a database connection, close it."""
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()



