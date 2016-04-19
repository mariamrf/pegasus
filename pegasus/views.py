from pegasus import app
import sqlite3
import uuid
import string
import random
from flask import request, session, g, redirect, url_for, abort, render_template, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from itertools import islice



# all the definitions
def get_random_string(length=32):
     return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))

def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = get_random_string()
    return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token

def login_user(username):
    session['logged_in'] = True
    session['username'] = username
    cur = g.db.execute('select id from users where username=?', [username]).fetchone()
    uid = cur[0]
    session['userid'] = uid # to register any info in another table where userid is a FK instead of querying every time


def is_owner(boardID, userID):
    cur = g.db.execute('select creatorID from boards where id=?', [boardID]).fetchone()[0]
    if cur == userID:
        return True
    else:
        return False

def is_authorized(boardID):
    access = False
    isOwner = False
    accessType = None
    if session.get('logged_in'):
        # not counting in the invitation link logic here
        uid = session['userid']
        # are they the owner?
        if is_owner(boardID, uid):
            access = True
            isOwner = True
            accessType = 'edit'
        else:
            uemail = g.db.execute('select email from users where id=?', [uid]).fetchone()[0]
            cur2 = g.db.execute('select type from invites where boardID=? and userEmail=?', [boardID, uemail]).fetchone()
            if cur2 is not None:
                access = True
                accessType = cur2[0]
    return {'access':access, 'isOwner':isOwner, 'accessType':accessType}




    
# routing (views)
@app.route('/')
def index():
    if session.get('logged_in'):
        email = g.db.execute('select email from users where id=?', [session['userid']]).fetchone()[0].lower()
        cur2 = g.db.execute('select id, title from boards where id in (select boardID from invites where userEmail=?)', [email]).fetchall()
        invitedLi = [dict(id=row[0], title=row[1]) for row in cur2]
        return render_template('show_list.html', invitedBoards=invitedLi)
    else:
        cur = g.db.execute('select username, join_date from users order by id')
        li = [dict(username=row[0], jdate=row[1]) for row in cur.fetchall()]
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
    if session.get('logged_in'):
        abort(401)
    error = None
    if request.method == 'POST':
        cur = g.db.execute('select username, password from users where username=?', [request.form['username'].lower()])
        cur_res = cur.fetchone()
        if cur_res is None:
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
    cur2 = g.db.execute('select id, title from boards where creatorID=?', [uid]).fetchall()
    boards = [dict(id=row[0], title=row[1]) for row in cur2]
    return render_template('profile.html', name=cur[0], email=cur[1], boards=boards)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('userid', None)
    flash('You go bye bye :(', 'warning')
    return redirect(url_for('index')) # always going there..

@app.route('/new-board', methods=['GET', 'POST'])
def create_board():
    if not session.get('logged_in'):
        abort(401)
    error = None
    if request.method == 'POST':
        try:
            uid = session.get('userid')
            title = request.form['title']
            done_at = datetime.utcnow() + timedelta(days=1)
            cur = g.db.cursor()
            cur.execute('insert into boards (creatorID, title, done_at) values (?, ?, ?)', [uid, title, done_at])
            g.db.commit()
            boardID = cur.lastrowid
            cur.close()
            return redirect(url_for('show_board', boardID=boardID))
        except sqlite3.Error as e:
            error = 'An error occured: ' + e.args[0]
    return render_template('new-board.html', error=error)

@app.route('/board/<boardID>')
def show_board(boardID):
    # first, check if there's even a board
    curB = g.db.execute('select title, created_at, done_at from boards where id=?', [boardID]).fetchone()
    if curB is None:
        abort(404)
    else:
        invite = request.args.get('invite') # ?invite=INVITE_ID
        auth = is_authorized(boardID)
        can_participate = False
        done_at = datetime.strptime(curB[2], '%Y-%m-%d %H:%M:%S.%f')
        isDone = False
        if(done_at < datetime.utcnow()):
            isDone = True
        if auth['access']: # don't care if there's an invite string as long as you have access while logged in
            if auth['accessType'] == 'edit':
                can_participate = True
            return render_template('show-board.html', canEdit=can_participate, isDone=isDone, title=curB[0], created_at=curB[1], done_at=curB[2], isOwner=auth['isOwner'], boardID=boardID)
        elif invite is not None:
            cur = g.db.execute('select userEmail, type from invites where id=? and boardID=?', [invite, boardID]).fetchone()
            if cur is None:
                abort(401)
            else:
                if cur[1] == 'edit':
                    can_participate = True
                return render_template('show-board.html', canEdit=can_participate, isDone=isDone, title=curB[0], created_at=curB[1], done_at=curB[2], email=cur[0], boardID=boardID)
        else:
            abort(401)


# AJAX functions
## GET
@app.route('/_validateUsername')
def valUsername():
    un = request.args.get('username', 0, type=str)
    cur = g.db.execute('select id from users where username=?', [un.lower()]).fetchone()
    if cur is None:
        return jsonify(available='true')
    else:
        return jsonify(available='false')

@app.route('/_validateEmail')
def valEmail():
    em = request.args.get('email', 0, type=str)
    cur = g.db.execute('select id from users where email=?', [em.lower()]).fetchone()
    if cur is None:
        return jsonify(available='true')
    else:
        return jsonify(available='false')


## POST
@app.route('/_editBoard', methods=['POST'])
def edit_board():
    if not session.get('logged_in'):
        abort(401)
    else: # is logged in
        error = 'None'
        new_token = generate_csrf_token()
        try:
            g.db.execute('update boards set title=? where id=? and creatorID=?', [request.form['title'], int(request.form['boardID']), session['userid']])
            g.db.commit()
        except sqlite3.Error as e:
            error = e.args[0]
        return jsonify(error=error, token=new_token) # and new CSRF token to be used again

@app.route('/_editProfile', methods=['POST'])
def edit_profile():
    if not session.get('logged_in'):
        abort(401)
    else:
        error = 'None'
        new_token = generate_csrf_token()
        cur = g.db.execute('select name, email, username from users where id=?', [session['userid']]).fetchone()
        old_name = cur[0]
        old_email = cur[1]
        old_username = cur[2]
        em = request.form['email'].lower()
        un = request.form['username'].lower()
        name = request.form['name']
        # first, check availability
        okay = True
        cur1 = g.db.execute('select id from users where email=?', [em]).fetchone()
        cur2 = g.db.execute('select id from users where username=?', [un]).fetchone()
        if cur1 is not None:
            if cur1[0] != session['userid']:
                okay = False
                error = 'Email is not available.'
        if cur2 is not None:
            if cur2[0] != session['userid']:
                okay = False
                if error == 'None':
                    error = 'Username is not available.'
                else:
                    error+='Username is not available.'
        if okay:
            if old_name != name or old_email != em or old_username != un: # only proceed if any changes were made
                try:
                    old_em = g.db.execute('select email from users where id=?', [session['userid']]).fetchone()[0].lower()
                    g.db.execute('update users set name=?, email=?, username=? where id=?', [name, em, un, session['userid']])
                    session['username'] = un;
                    g.db.execute('update invites set userEmail=? where userEmail=?', [em, old_em])
                    g.db.commit()
                except sqlite3.Error as e:
                    error = e.args[0]
        return jsonify(error=error, token=new_token)

@app.route('/_changePassword', methods=['POST'])
def change_password(): 
    if not session.get('logged_in'):
        abort(401)
    else:
        error = 'None'
        new_token = generate_csrf_token()
        password = generate_password_hash(request.form['password'])
        pw = g.db.execute('select password from users where id=?', [session['userid']]).fetchone()[0]
        if not check_password_hash(pw, request.form['old-password']):
            error = 'Old password you entered is incorrect.'
        else: 
            try:
                g.db.execute('update users set password=? where id=?', [password, session['userid']])
                g.db.commit()
            except sqlite3.Error as e:
                error = e.args[0]
        return jsonify(error=error, token=new_token)

@app.route('/_markDone', methods=['POST'])
def mark_done():
    if not session.get('logged_in'):
        abort(401)
    else:
        error = 'None'
        new_token = generate_csrf_token()
        done_at = datetime.utcnow()
        bid = int(request.form['boardID'])
        old_done_at = datetime.strptime(g.db.execute('select done_at from boards where id=?', [bid]).fetchone()[0], '%Y-%m-%d %H:%M:%S.%f')
        if old_done_at < done_at:
            abort(400)
        try:
            g.db.execute('update boards set done_at=? where id=? and creatorID=?', [done_at, bid, session['userid']])
            g.db.commit()
        except sqlite3.Error as e:
            error = e.args[0]
        return jsonify(error=error, token=new_token)

@app.route('/_inviteUser', methods=['POST'])
def invite_user():
    if not session.get('logged_in'):
        abort(401)
    em = request.form['email'].lower()
    ty = request.form['type'] # view or edit
    b_id = int(request.form['boardID'])
    user = session['userid']
    inviteID = uuid.uuid4().hex
    error = 'None'
    successful='false'
    if is_owner(b_id, user):
        try:
            g.db.execute('insert into invites (id, userEmail, boardID, type) values (?, ?, ?, ?)', [inviteID, em, b_id, ty])
            g.db.commit()
            successful = 'true'
        except sqlite3.IntegrityError as e:
            error = 'This email has already been invited to this board.'
        except sqlite3.Error as e: # for debugging
            error = e.args[0]
        finally:
            new_token = generate_csrf_token()
    return jsonify(successful=successful, error=error, token=new_token)

## API (GET/POST)
@app.route('/api/board/<boardID>/components', methods=['GET', 'POST']) # just all the components with everything there is to know about them for this phase
def board_components(boardID):
    # first of all, authenticate
    bid = int(boardID)
    cur0 = g.db.execute('select title from boards where id=?', [bid]).fetchone()
    ## If board doesn't exist
    if cur0 is None:
        abort(404)
    ## If there's an invite code
    if request.method == 'GET':
        inv = request.args.get('invite', 0, str)
    else:
        inv = request.form['invite']
    if inv != '-1' and not session.get('logged_in'): # don't care if there's an invite string as long as they're logged in
        cur = g.db.execute('select type, userEmail from invites where id=? and boardID=?', [inv, bid]).fetchone()
        if cur is None:
            abort(401)
    else:
        auth = is_authorized(bid)
        if not auth['access']:
            abort(401)
    ### GET COMPONENTS
    if request.method == 'GET':
        # no need for extra auth here as everyone with access to the board can see everything
        cur2 = g.db.execute('select id, content, userID, userEmail, created_at from board_content where boardID=? order by created_at', [bid]).fetchall()
        if len(cur2) > request.args.get('number', 0, int): # this only works because nobody can delete a message, obvs not good for the long run
            messages_sliced = islice(cur2, request.args.get('number', 0, int), None)
            messages = [dict(id=row[0], content=row[1], userID=row[2], userEmail=row[3], created_at=row[4]) for row in messages_sliced]
            return jsonify(messages=messages)
        else:
            er = 'No new'
            return jsonify(error=er)
    ### POST A SINGLE COMPONENT/MESSAGE
    elif request.method == 'POST':
        new_token = generate_csrf_token()
        msg = request.form['message']
        error = 'None'
        curDone = g.db.execute('select done_at from boards where id=?', [bid]).fetchone()
        done_at = datetime.strptime(curDone[0], '%Y-%m-%d %H:%M:%S.%f')
        if(done_at > datetime.utcnow()):
            if session.get('logged_in'):
                try:
                    g.db.execute('insert into board_content (boardID, userID, content) values (?, ?, ?)', [bid, session['userid'], msg])
                    g.db.commit()
                except sqlite3.Error as e:
                    error = e.args[0]
            else: # has an invite, if they made it this far
                ty = cur[0]
                em = cur[1]
                if ty != 'edit':
                    abort(401)
                try:
                    g.db.execute('insert into board_content (boardID, userEmail, content) values (?, ?, ?)', [bid, em, msg])
                    g.db.commit()
                except sqlite3.Error as e:
                    error = e.args[0]
        else:
            error = 'This board was marked as done by its creator, you cannot make any more changes.'
        return jsonify(error=error, token=new_token)


@app.route('/api/user/<userID>', methods=['GET'])
def get_user(userID):
    # no authentication needed, public info. A better app would only provide this info to people who have something in common with the user
    ## like they share a board. But for now, it's just public.
    error = 'None'
    username = None
    name = None
    try:
        cur = g.db.execute('select name, username from users where id=?', [int(userID)]).fetchone()
        if cur is None:
            error = 'User not found.'
        else:
            name = cur[0]
            username = cur[1]
    except sqlite3.Error as e: # just in case
        error = e.args[0]
    return jsonify(error=error, username=username, name=name)
