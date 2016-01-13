import setup
import unittest
from goly import app
from goly.models.user import User
import json

class TestUserApi(unittest.TestCase):
    test_client = app.test_client()
    new_user = {"email": "test@example.com", "password": "test-pass", "first_name": "first", "last_name": "last"}
    def setUp(self):
        User.query.delete()

    def tearDown(self):
        User.query.delete()
    
    def test_register(self):
        tc = self.test_client
        res = tc.post("/register", data=self.new_user)
        self.assertOk(res)
        data = json.loads(res.data)
        self.assertIn('id', data)
        for field, value in self.new_user.iteritems():
            if (field == 'password'): self.assertNotIn(field, data)
            else: self.assertEqual(value, data[field])

        ## you should get a well-formatted error if the user already exists.
        self.new_user['password'] = "new-test-pass"
        res = tc.post("/register", data=self.new_user)
        self.assertEqual(res.status_code, 409)
        data = json.loads(res.data)
        self.assertIn('detail', data)
        self.assertIn('test@example.com already exists', data['detail'])
        self.new_user['password'] = "test-pass"

    def test_destroy(self):
        user = User(self.new_user['email'], self.new_user['password'], self.new_user['first_name'], self.new_user['last_name'])
        user.persist()
        self.assertTrue(user.exists()) ## I don't understand why but this is necessary or else line 45 fails

        tc = self.test_client
        res = tc.post("/user/delete", data={"email": "fake email", "password": "test-pass"})
        data = json.loads(res.data)
        self.assertInvalidCredentials(res)
        self.assertTrue(user.exists())

        tc = self.test_client
        res = tc.post("/user/delete", data={"email": user.email, "password": "nottherightpass"})
        data = json.loads(res.data)
        self.assertInvalidCredentials(res)
        self.assertTrue(user.exists())

        res = tc.post("/user/delete", data={"email": user.email, "password": "test-pass"})
        self.assertOk(res)
        self.assertFalse(user.exists())

    def test_login(self):
        tc = self.test_client
        res = tc.post('/register', data=self.new_user)

        res = tc.post('/login', data={"email": "notreal", "password": self.new_user['password']})
        data = json.loads(res.data)
        self.assertIn('detail', data)
        self.assertIn('notreal is not a registered', data['detail'])
        self.assertEqual(res.status_code, 401)

        res = tc.post('/login', data={"email": self.new_user['email'], "password": "notpass"})
        data = json.loads(res.data)
        self.assertIn('detail', data)
        self.assertIn('Incorrect password', data['detail'])
        self.assertEqual(res.status_code, 401)

        res = tc.post('/login', data={"email": self.new_user['email'], "password": self.new_user['password']})
        self.assertOk(res)

    def test_update_password(self):
        tc = self.test_client
        res = tc.post("/register", data=self.new_user)
        self.assertOk(res)

        ## should fail for non-existent emails
        res = tc.post('/user/update-password', data={"email": "notreal", "old_password": "test-pass", "new_password": "new-pass"})
        self.assertInvalidCredentials(res)

        res = tc.post('/user/update-password', data={"email": self.new_user['email'], "old_password": "notreal", "new_password": "new-pass"})
        self.assertInvalidCredentials(res)

        res = tc.post('/user/update-password', data={"email": self.new_user['email'], "old_password": self.new_user['password'], "new_password": "new-pass"})
        self.assertOk(res)
        res = tc.post("/login", data={"email": self.new_user['email'], "password": "new-pass"})
        self.assertOk(res)

    def assertInvalidCredentials(self, res):
        """Logic for asserting that credentials passed were invalid"""
        data = json.loads(res.data)
        self.assertIn('detail', data)
        self.assertIn('Invalid credentials', data['detail'])
        self.assertEqual(res.status_code, 401)

    def assertOk(self, res):
        self.assertEqual(res.status_code, 200)



if __name__ == '__main__':
    unittest.main()