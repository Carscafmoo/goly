import setup
import unittest
from goly import app, db
from goly.models.user import User
import json

class TestUserApi(unittest.TestCase):
    test_client = app.test_client()
    new_user = {"email": "test@example.com", "password": "test-pass", "first_name": "first", "last_name": "last"}
    def setUp(self):
        User.query.delete()
        db.session.commit()
        
    def tearDown(self):
        User.query.delete()
        db.session.commit()
    
    def test_register(self):
        tc = self.test_client
        invalid_user = {}
        for x, y in self.new_user.iteritems():
            if x != 'password': invalid_user[x] = y 
        
        res = tc.post('/register', data=invalid_user)
        self.assertInvalid(res, 'password')
        
        res = tc.post("/register", data=self.new_user)
        self.assertOk(res, 201)
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
        res = tc.post("/users/delete", data={"email": "fake email"})
        self.assertInvalid(res, 'password')

        res = tc.post("/users/delete", data={"email": "fake email", "password": "test-pass"})
        data = json.loads(res.data)
        self.assertInvalidCredentials(res)
        self.assertTrue(user.exists())

        tc = self.test_client
        res = tc.post("/users/delete", data={"email": user.email, "password": "nottherightpass"})
        data = json.loads(res.data)
        self.assertInvalidCredentials(res)
        self.assertTrue(user.exists())

        res = tc.post("/users/delete", data={"email": user.email, "password": "test-pass"})
        self.assertOk(res, 204)
        self.assertFalse(user.exists())

    def test_login(self):
        tc = self.test_client
        res = tc.post('/register', data=self.new_user)

        res = tc.post('/login', data={"email": self.new_user['email']})
        self.assertInvalid(res, 'password')

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
        self.assertOk(res, 201)

    def test_update_password(self):
        tc = self.test_client
        res = tc.post("/register", data=self.new_user)
        self.assertOk(res, 201)

        ## Shoudl fail if missing a key
        res = tc.post('/users/update-password', data={"email": self.new_user['email'], "new_password": "test"})
        self.assertInvalid(res, 'old_password')

        ## should fail for non-existent emails
        res = tc.post('/users/update-password', data={"email": "notreal", "old_password": "test-pass", "new_password": "new-pass"})
        self.assertInvalidCredentials(res)

        res = tc.post('/users/update-password', data={"email": self.new_user['email'], "old_password": "notreal", "new_password": "new-pass"})
        self.assertInvalidCredentials(res)

        res = tc.post('/users/update-password', data={"email": self.new_user['email'], "old_password": self.new_user['password'], "new_password": "new-pass"})
        self.assertOk(res)
        res = tc.post("/login", data={"email": self.new_user['email'], "password": "new-pass"})
        self.assertOk(res, 201)

    def test_get_me(self):
        tc = self.test_client
        res = tc.get('/users/me') ## Should return anonymous user
        self.assertRequiresLogin(res)
        
        res = tc.post('/register', data=self.new_user)
        self.assertOk(res, 201)
        data = json.loads(res.data)
        
        res = tc.post('/login', data={"email": self.new_user['email'], "password": self.new_user['password']})
        self.assertOk(res, 201)

        res = tc.get('/users/me')
        self.assertOk(res)
        for key in ["registered_on", "first_name", "last_name", "id", "email"]:
            self.assertIn(key, data)
            if (key in self.new_user):
                self.assertEqual(self.new_user[key], data[key])

        res = tc.post('/logout')
        res = tc.get('/users/me') ## Should return anonymous user
        self.assertRequiresLogin(res)

    def test_get_user(self):
        tc = self.test_client
        res = tc.get('/users/1')
        self.assertRequiresLogin(res)

        res = tc.post('/register', data=self.new_user)
        self.assertOk(res, 201)
        user_data = json.loads(res.data)
        
        res = tc.post('/login', data={"email": self.new_user['email'], "password": self.new_user['password']})
        self.assertOk(res, 201)

        res = tc.get('/users/' + str(user_data['id']))
        self.assertOk(res)
        self.assertEqual(user_data, json.loads(res.data))

        res = tc.get('/users/0')
        self.assertEqual(res.status_code, 404)

    def assertInvalidCredentials(self, res):
        """Logic for asserting that credentials passed were invalid"""
        data = json.loads(res.data)
        self.assertIn('detail', data)
        self.assertIn('Invalid credentials', data['detail'])
        self.assertEqual(res.status_code, 401)

    def assertOk(self, res, code=200):
        self.assertEqual(res.status_code, code)

    def assertRequiresLogin(self, res):
        self.assertEqual(res.status_code, 401)
        data = json.loads(res.data)
        self.assertIn('detail', data)
        self.assertIn("You must login to view this page", data['detail'])

    def assertInvalid(self, res, missing_field):
        self.assertEqual(res.status_code, 400)
        data = json.loads(res.data)
        self.assertIn('detail', data)
        self.assertIn(missing_field, data['detail'])

if __name__ == '__main__':
    unittest.main()