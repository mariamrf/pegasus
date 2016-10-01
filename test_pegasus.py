#!/usr/bin/env python3
import os
import pegasus
import unittest
import tempfile

class PegasusTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, pegasus.app.config['DATABASE'] = tempfile.mkstemp()
        pegasus.app.config['TESTING'] = True
        self.app = pegasus.app.test_client()
        with pegasus.app.app_context():
            pegasus.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(pegasus.app.config['DATABASE'])

if __name__ == '__main__':
    unittest.main()