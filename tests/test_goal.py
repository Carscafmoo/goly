import setup
import unittest
from goly.models.goal import Goal
from goly.models.user import User
import json
import goly.errors

class TestGoal(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.test_user = setup.create_test_user()

    @classmethod
    def tearDownClass(self):
        User.query.delete()

    def setUp(self):
        Goal.query.delete()

    def tearDown(self):
        User.query.delete()

    def test_init(self):
        ## Test that all of the validators work!
        fake_user = User("notreal", "notreal", "notreal", "notreal")
        with self.assertRaisesRegexp(AssertionError, "user does not exist"):
            goal = Goal(fake_user, "test name", "weekly", 10, "binary")

        with self.assertRaisesRegexp(AssertionError, "user must be a User"):
            goal = Goal("Jimmy", "test", "weekly", 10, "binary")

        """@TODO: the rest of these        @validates("user")
        def validate_user(self, key, user):
            assert isinstance(user, User)
            assert user.exists()

        @validates("name")
        def validate_name(self, key, name):
            length = len(name)
            assert length > 0 and length <= 50

        @validates("frequency")
        def validate_target(self, key, freq):
            assert freq in ['day', 'week', 'month', 'quarter', 'year']

        @validates("target")
        def validate_frequency(self, key, target):
            assert isinstance(target, (int, long)) or (isinstance(target, str) and freq.isdigit())

        @validates("input_type")
        def validate_input_type(self, key, it):
            assert it in ['binary', 'numeric']

        @validates("active")
        def validate_active(self, key, active):
            assert isinstance(active, bool)

        @validates("public")
        def validate_public(self, key, public):
            assert isinstance(public, bool)"""


