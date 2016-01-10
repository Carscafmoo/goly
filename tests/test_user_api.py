import setup
import unittest
from goly import app
from goly.models.user import User
import json

class TestUserApi(unittest.TestCase):
    test_client = app.test_client()
    def setUp(self):
        User.query.delete()

    def tearDown(self):
        User.query.delete()
    
    def test_register(self):
        tc = self.test_client
        new_user = {"email": "test@example.com", "password": "test-pass", "first_name": "first", "last_name": "last"}
        res = tc.post("/register", data=new_user)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn('id', data)
        for field, value in new_user.iteritems():
            if (field == 'password'): self.assertNotIn(field, data)
            else: self.assertEqual(value, data[field])

        ## you should get a well-formatted error if the user already exists.
        new_user['password'] = "new-test-pass"
        res = tc.post("/register", data=new_user)
        self.assertEqual(res.status_code, 409)
        data = json.loads(res.data)
        self.assertIn('detail', data)
        self.assertIn('test@example.com already exists', data['detail'])

if __name__ == '__main__':
    unittest.main()