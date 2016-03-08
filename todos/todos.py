# imports here
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing

# config (which should be in another file for larger apps)
DATABASE = '/tmp/todos.db'
DEBUG = True
SECRET_KEY = 'you shall not pass'
USERNAME = 'scott'
PASSWORD = 'tiger' # Oracle may or may have not branded this into me

# initialize app
app = Flask(__name__)
app.config.from_object(__name__) # or the other file if we had the config in another file (ref: app.config.from_envvar('FLASKR_SETTINGS', silent=True))

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

@app.teardown_request
def teardown_request(exception):
	db = getattr(g, 'db', None)
	if db is not None:
		db.close()

# routing (views)
@app.route('/')
def show_list():
	cur = g.db.execute('select content from items order by id')
	li = [dict(content=row[0]) for row in cur.fetchall()]
	return render_template('show_list.html', li=li)

@app.route('/add', methods=['POST'])
def add_item():
	if not session.get('logged_in'):
		abort(401)
	g.db.execute('insert into items (content) values (?)', [request.form['content']])
	g.db.commit()
	flash('New entry was successfully posted!') # what happens if we're unsuccessful?
	return redirect(url_for('show_list'))

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME']: # because no user table. Sad.
		    error = 'Invalid username'
		elif request.form['password'] != app.config['PASSWORD']: # ouch
			error = 'Invalid password'
		else:
			session['logged_in'] = True
			flash('Hey there!')
			return redirect(url_for('show_list'))
	return render_template('login.html', error=error)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You go bye bye :(')
	return redirect(url_for('show_list')) # always going there..




# le boilerplate
if __name__ == '__main__':
	app.run()


