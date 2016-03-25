#!/usr/bin/env python3
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from werkzeug.security import generate_password_hash, check_password_hash
from contextlib import closing

# config (which should be in another file for larger apps)
DATABASE = '/tmp/pegasus.db'
DEBUG = True
SECRET_KEY = 'you shall not pass'


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

def login_user(username):
    session['logged_in'] = True
    session['username'] = username

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
    cur = g.db.execute('select username, join_date from users order by id')
    li = [dict(username=row[0], jdate=row[1]) for row in cur.fetchall()]
    # li = [{'name': 'hello'}, {'name': 'hi'}]
    return render_template('show_list.html', li=li)

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if session.get('logged_in'):
        abort(401)
    error = None
    if request.method == 'POST':
        try:
            pw = generate_password_hash(request.form['password'])
            g.db.execute('insert into users (username, password, email, name) values (?, ?, ?, ?)', [request.form['username'], pw, request.form['email'], request.form['name']])
            g.db.commit()
            login_user(request.form['username'])
            return redirect(url_for('show_list'))
        except sqlite3.IntegrityError as e:
        	if e.args[0][32:] == 'email':
        		error = 'Email'
        	elif e.args[0][32:] == 'username':
        		error = 'Username'
        	error = error + ' already in use.'
    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        cur = g.db.execute('select username, password from users where username=?', [request.form['username']])
        cur_res = cur.fetchone()
        if cur_res == None:
            error = 'Invalid username'
        else:
            username = cur_res[0]
            pw = cur_res[1]
            if check_password_hash(pw, request.form['password']) == False: # ouch
                error = 'Invalid password'
            else:
                login_user(username)
                flash('Hey there!', 'info')
                return redirect(url_for('show_list'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You go bye bye :(', 'warning')
    return redirect(url_for('show_list')) # always going there..




# le boilerplate
if __name__ == '__main__':
    app.run()


