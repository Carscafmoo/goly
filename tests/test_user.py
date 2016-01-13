import setup
import unittest
from goly.models.user import User
import json
import goly.errors

class TestUser(unittest.TestCase):
    def setUp(self):
        User.query.delete()
        self.new_user = User("test@example.com", "test-pass", "first", "last")

    def tearDown(self):
        User.query.delete()

    def test_init(self):
        self.assertEqual(self.new_user.email, "test@example.com")
        self.assertNotEqual(self.new_user.password, "test-pass") # Should be hashed
        self.assertEqual(self.new_user.first_name, "first")
        self.assertEqual(self.new_user.last_name, "last")

    def test_full_name(self):
        self.assertEqual(self.new_user.full_name(), "first last")

    def test_persist_and_destroy(self):
        self.assertFalse(self.new_user.exists())
        self.new_user.persist()
        self.assertTrue(self.new_user.exists())

        test_user = User.pull_by_id(self.new_user.get_id())
        self.assertEqual(test_user, self.new_user)

        test_user = User.pull_by_email(self.new_user.email)
        self.assertEqual(test_user, self.new_user)

        self.new_user.destroy()
        self.assertFalse(self.new_user.exists())

    def test_update_password(self):
        self.new_user.update_password("test-pass", "new-test-pass")
        self.assertTrue(self.new_user.check_password("new-test-pass"))
        self.new_user.update_password("new-test-pass", "test-pass")
        with self.assertRaises(goly.errors.UnauthorizedError):
            self.new_user.update_password("not-my-password", "new-test-pass")

        self.new_user.persist()
        self.new_user.update_password("test-pass", "new-test-pass")
        self.assertFalse(self.new_user.check_password("test-pass"))
        self.assertTrue(self.new_user.check_password("new-test-pass"))
        self.assertTrue(self.new_user.exists())

        user = User.pull_by_id(self.new_user.get_id())
        self.assertTrue(user.check_password("new-test-pass"))


if __name__ == '__main__':
    unittest.main()