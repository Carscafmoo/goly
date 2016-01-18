import setup
import unittest
from goly import app, db
from goly.models.user import User
import json
import datetime

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

    def test_update_email(self):
        tc = self.test_client
        post_data = {"old_email": self.new_user['email'], "new_email": "test-new-email@example.com", "password": self.new_user['password']}
        res = tc.post('/users/update-email', data=post_data)
        self.assertInvalidCredentials(res)

        res = tc.post('/register', data=self.new_user)
        self.assertOk(res, 201)

        post_data['password'] = 'not-my-pass'
        res = tc.post('/users/update-email', data=post_data)
        self.assertInvalidCredentials(res)

        post_data['password'] = None
        res = tc.post('/users/update-email', data=post_data)
        self.assertInvalid(res, 'password')

        post_data['password'] = self.new_user['password']
        res = tc.post('/users/update-email', data=post_data)
        self.assertOk(res)

        res = tc.post('/login', data={"email": post_data['new_email'], "password": post_data['password']})
        self.assertOk(res, 201)

    def test_update(self):
        tc = self.test_client

        res = tc.post('/register', data=self.new_user)
        self.assertOk(res, 201)
        user = json.loads(res.data)

        post_data = {"password": self.new_user['password'], "first_name": "new-first-name"}

        res = tc.post('/users/update', data=post_data)
        self.assertInvalid(res, 'email')

        post_data['email'] = "not-real-email"
        res = tc.post('/users/update', data=post_data)
        self.assertInvalidCredentials(res)        

        post_data['email'] = self.new_user['email']
        post_data['password'] = 'not-real-pass'
        res = tc.post('/users/update', data=post_data)
        self.assertInvalidCredentials(res)    

        post_data['password'] = self.new_user['password']
        res = tc.post('/users/update', data=post_data)
        self.assertOk(res)

        res = tc.post('/login', data={'email': self.new_user['email'], 'password': self.new_user['password']})
        self.assertOk(res, 201)
        res = tc.get('/users/me')
        self.assertOk(res)
        updated_user = json.loads(res.data)
        for key, value in user.iteritems():
            if (key == 'first_name'): self.assertEqual(updated_user[key], 'new-first-name')
            else: self.assertEqual(updated_user[key], user[key])

    def test_get_index(self):
        tc = self.test_client
        res = tc.get('/users/index')
        self.assertRequiresLogin(res)

        setup.create_test_users()
        res = tc.post('/login', data={'email': "test_a@example.com", 'password': self.new_user['password']})
        self.assertOk(res, 201)

        res = tc.get('/users/index')
        self.assertOk(res)
        data = json.loads(res.data)
        self.assertIn('users', data)
        data = data['users']
        self.assertEqual(len(data), 20) # default is 20
        for x in range(ord('a'), ord('a') + 19):
            self.assertEqual(data[x - ord('a')]['email'], 'test_' + chr(x) + '@example.com') ## Should sort by email 

        res = tc.get('/users/index?count=3&offset=3')
        self.assertOk(res)
        data = json.loads(res.data)
        self.assertIn('users', data)
        data = data['users']
        self.assertEqual(len(data), 3)
        for x in range(ord('a'), ord('a') + 2):
            self.assertEqual(data[x - ord('a')]['email'], 'test_' + chr(x + 3) + '@example.com') ## Should still sort by email 

        res = tc.get('/users/index?count=3&offset=3&sort=last_name&sort_order=desc')
        self.assertOk(res)
        data = json.loads(res.data)
        self.assertIn('users', data)
        data = data['users']
        self.assertEqual(len(data), 3)
        for x in range(ord('a'), ord('a') + 2):
            self.assertEqual(data[x - ord('a')]['email'], 'test_' + chr(2 * ord('a') + 25 - x - 3) + '@example.com')


        res = tc.get('/users/index?count=3&offset=3&sort=not_a_real_field&sort_order=desc')
        self.assertInvalid(res, 'sort')
        
        res = tc.get('/users/index?count=3&offset=3&sort=last_name&sort_order=pineapple')
        self.assertInvalid(res, 'sort_order')
        
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