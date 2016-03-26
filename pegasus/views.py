from pegasus import app
import sqlite3
from flask import request, session, g, redirect, url_for, abort, render_template, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash


def login_user(username):
    session['logged_in'] = True
    session['username'] = username
    cur = g.db.execute('select id from users where username=?', [username]).fetchone()
    uid = cur[0]
    session['userid'] = uid # to register any info in another table where userid is a FK instead of querying every time
    
# routing (views)
@app.route('/')
def index():
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
            un = request.form['username'].lower()
            em = request.form['email'].lower()
            g.db.execute('insert into users (username, password, email, name) values (?, ?, ?, ?)', [un, pw, em, request.form['name']])
            g.db.commit()
            login_user(un)
            return redirect(url_for('index'))
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
        cur = g.db.execute('select username, password from users where username=?', [request.form['username'].lower()])
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
                return redirect(url_for('index'))
    return render_template('login.html', error=error)

@app.route('/profile')
def show_profile():
	if not session.get('logged_in'):
		abort(401)
	uid = session.get('userid')
	cur = g.db.execute('select name, email from users where id=?', [uid]).fetchone()
	return render_template('profile.html', name=cur[0], email=cur[1])

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('userid', None)
    flash('You go bye bye :(', 'warning')
    return redirect(url_for('index')) # always going there..

# AJAX functions
@app.route('/_validateUsername')
def valUsername():
	un = request.args.get('username', 0, type=str)
	cur = g.db.execute('select id from users where username=?', [un.lower()]).fetchone()
	if cur==None:
		return jsonify(available='true')
	else:
		return jsonify(available='false')

@app.route('/_validateEmail')
def valEmail():
	em = request.args.get('email', 0, type=str)
	cur = g.db.execute('select id from users where email=?', [em.lower()]).fetchone()
	if cur==None:
		return jsonify(available='true')
	else:
		return jsonify(available='false')

