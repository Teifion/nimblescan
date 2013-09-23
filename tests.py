import unittest
from datetime import date, datetime, timedelta
import transaction

from .models import NimblescanCache
from . import api, lib

from .config import config

"""
I've got a class defined in test_f which does the following.

class DBTestClass(unittest.TestCase):
    def setUp(self):
        self.session = _initTestingDB()
        self.config = routes(testing.setUp())
    
    def tearDown(self):
        DBSession.execute("ROLLBACK")
        self.session.remove()
    
    def get_app(self, auth):
        # Auth is a username of the user you're authing as
        # Code that returns a testapp and cookie data
    
    def make_request(self, app, path, data, msg="", expect_forward=False):
        # Makes a request and checks for errors
        # Provides a custome message on failure
        # Allows expected fowards

Sadly I couldn't work out how to detatch this part from my
main framework. The key part is it'll allow us to use the db connection.
"""

try:
    from ..core.lib.test_f import DBTestClass
except Exception:
    class DBTestClass(object):
        pass

# We assume this is the user your system will grab for us
user_id = 1

class NimblescanCacheTester(DBTestClass):
    def test_lifecycle(self):
        # Reset handlers, just to be sure
        config['handlers'] = {}
        
        # We'll need these later
        app, cookies = self.get_app()
        
        # Register them, the test_register function below tests the accuracy of this
        api.register('nimblescan.f1', 'NS One', ['term 1'], (lambda r: True), api.make_forwarder("nimblescan.f1"))
        
        # Clear all existing notifications
        lib.flush(user_id)
        
        # Make sure that worked
        cache_list = list(config['DBSession'].query(NimblescanCache).filter(NimblescanCache.user == user_id))
        self.assertEqual(len(cache_list), 0)
        
        # Now build a new one
        page_result = self.make_request(
            app,
            "/nimblescan/list",
            cookies,
            "There was an error viewing the list"
        )

class FunctionalTester(unittest.TestCase):
    def test_register(self):
        # Reset handlers, just to be sure
        config['handlers'] = {}
        
        api.register('nimblescan.f1', 'NS One', ['term 1'], (lambda r: True), api.make_forwarder("nimblescan.f1"))
        api.register('nimblescan.f2', 'NS Two', ['term 2'], (lambda r: True), api.make_forwarder("nimblescan.f2"))
        
        # Check it won't let us overwrite an existing registrant
        self.assertRaises(KeyError, api.register, 'nimblescan.f1', 'NS Three', ['term 3'], (lambda r: True), api.make_forwarder("nimblescan.f3"), raise_on_dupe=True)
        
        self.assertEqual(len(config['handlers']), 2)
        self.assertIn('nimblescan.f1', config['handlers'])
        self.assertNotIn('nimblescan.f3', config['handlers'])
