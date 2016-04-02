#!/usr/bin/env python3
import sqlite3
from flask import Flask, g, request, session, abort
from contextlib import closing

# config (which should be in another file for larger apps)
DATABASE = '/tmp/pegasus.db'
DEBUG = True
SECRET_KEY = 'you shall not pass'


# initialize app
app = Flask(__name__)
app.config.from_object(__name__) # or the other file if we had the config in another file (ref: app.config.from_envvar('FLASKR_SETTINGS', silent=True))

# import other necessary modules
import pegasus.views
import pegasus.errorhandlers

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()



# database requests
@app.before_request
def before_request():
    g.db = connect_db()

@app.before_request
def csrf_protect():
	if request.method == 'POST': # GET/ajax protection can be defined in their respective functions
		token = session.pop('_csrf_token', None)
		if not token or token != request.form.get('_csrf_token'):
			abort(400) 

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()



