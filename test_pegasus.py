"""
Tests
-----
This module contains all the tests related to the app.
"""

#!/usr/bin/env python3
import os
import pegasus
import unittest
import tempfile
from bs4 import BeautifulSoup

class PegasusTestCase(unittest.TestCase):

    def setUp(self):
        """
        Set up the test environment:
        1. Create a database temp file
        2. Enable testing
        3. Disable csrf protection
        4. Initialize the database
        """
        self.db_fd, pegasus.app.config['DATABASE'] = tempfile.mkstemp()
        pegasus.app.config['TESTING'] = True
        pegasus.app.config['CSRF_ENABLED'] = False
        self.app = pegasus.app.test_client()
        with pegasus.app.app_context():
            pegasus.init_db()

    def tearDown(self):
        """Close the test environment"""
        os.close(self.db_fd)
        os.unlink(pegasus.app.config['DATABASE'])

    def register(self, name, username, password, email):
        """Register a new user"""
        return self.app.post('/register', data = dict(
            name = name,
            username = username,
            password = password,
            email = email
            ), follow_redirects = True)

    def get_csrf(self):
        """Get current CSRF token (if needed for a test)"""
        rv = self.app.get('/')
        soup = BeautifulSoup(rv.data, 'html.parser')
        tag = soup.body.find('input', attrs = { 'name' : '_csrf_token'})
        return tag['value']


    def login(self, username, password):
        """Login into a registered account"""
        return self.app.post('/login', data = dict(
            username = username,
            password = password
            ), follow_redirects = True)

    def logout(self):
        """Logout from current login"""
        return self.app.get('/logout', follow_redirects = True)

    def create(self, title):
        """Create a new board while logged in"""
        return self.app.post('/new-board', data = dict(
            title = title
            ), follow_redirects = True)

    def show_board(self, boardID):
        """Show board with a certain ID"""
        return self.app.get('/board/' + boardID, follow_redirects = True)

    def edit_profile(self, name, username, email):
        """Edit logged in user's profile (without password)"""
        return self.app.post('/_editProfile', data = dict(
            name = name,
            username = username,
            email = email
            ), follow_redirects = True)

    def change_password(self, old_password, new_password):
        """Edit logged in user's password"""
        data = dict(password = new_password)
        data['old-password'] = old_password
        return self.app.post('/_changePassword', data = data, follow_redirects = True)

    def test_basic_ops(self):
        """
        Sequence of tests divided into categories:
        1. Registration
            a. Be able to register a user
            b. Be able to log out
            c. Get an error when registering an existing username
            d. Get an error when registering an existing email
        2. Login
            a. Get an error when the wrong password is entered
            b. Get an error when a non-existing username is entered
            c. Log in successfully
        3. Edit Profile
            a. Be able to edit name, username, and/or email if no conflict
            b. Get an error if a username exists, regardless of capitals
            c. Get an error if an email exists, regardless of capitals
            d. Get an error if both an email and a username exist, regardless of capitals
            e. Be able to change the password
            f. Get an error if the old password entered is incorrect
        4. Board Creation
            a. Be able to create a board when logged in.
            b. Be able to show that board.
            c. Get a 404 error if attempting to show a board that does not exist
        """
        success = 'OK'
        # 1. Register
        prefix = '[REGISTRATION]: '
        rv = self.register('Scott', 'scott', 'tiger123', 'scott@tiger.org')
        assert b'Successfully registered!' in rv.data
        rv = self.logout()
        assert b'You go bye bye :(' in rv.data
        rv = self.register('Scott', 'scott', 'tiger111', 'scott2@tiger.org')
        assert b'Username already in use' in rv.data
        rv = self.register('Scott', 'scott2', 'tiger113', 'scott@tiger.org')
        assert b'Email already in use' in rv.data
        ## Create another user for other tests
        self.register('Tammy', 'tammy', 'catfish122', 'tammy@catfish.org')
        self.logout()
        print(prefix + success)
        # 2. Login
        prefix = '[LOGIN]: '
        rv = self.login('scott', 'tiger111')
        assert b'Invalid password' in rv.data
        rv = self.login('notscott', 'tiger123')
        assert b'Invalid username' in rv.data
        rv = self.login('scott', 'tiger123')
        assert b'Hey there!' in rv.data
        print(prefix + success)
        # 3. Edit Profile
        prefix = '[EDIT PROFILE]: '
        rv = self.edit_profile('NOT SCOTT OK', 'scott', 'scott@tiger.org')
        assert b'None' in rv.data
        rv = self.edit_profile('NOT SCOTT OK', 'tamMy', 'scott@tiger.org')
        assert b'Username is not available' in rv.data
        rv = self.edit_profile('NOT SCOTT OK', 'scott', 'tammy@CATFISH.org')
        assert b'Email is not available' in rv.data
        rv = self.edit_profile('NOT SCOTT OK', 'tammy', 'tammy@catfish.org')
        assert b'Email is not available. Username is not available.' in rv.data
        rv = self.change_password('tiger123', 'tiger')
        assert b'None' in rv.data
        rv = self.change_password('nottiger', 'tiger123')
        assert b'Old password you entered is incorrect.' in rv.data
        print(prefix + success)
        # 4. Board Create/Show
        prefix = '[BOARD CREATION]: '
        rv = self.create('New Board')
        assert b'Board successfully created!' in rv.data
        rv = self.show_board('1')
        assert b'New Board' in rv.data
        rv = self.show_board('2')
        assert rv.status == '404 NOT FOUND'
        print(prefix + success)





if __name__ == '__main__':
    unittest.main()