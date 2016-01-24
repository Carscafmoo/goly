import setup
import unittest
from goly import app, db
from goly.models.user import User
from goly.models.goal import Goal
import json
import datetime

class TestUserApi(unittest.TestCase):
    test_client = app.test_client()
    new_goal = {"name": "Test goal", "prompt": "How many new goals did you create today?", "frequency": "daily", "target": 1, "input_type": "numeric"}

    @classmethod
    def setUpClass(self):
        User.query.delete()
        db.session.commit()
        setup.create_test_user()
        

    @classmethod
    def tearDownClass(self):
        User.query.delete()
        db.session.commit()

    def setUp(self):
        Goal.query.delete()
        db.session.commit()

    def tearDown(self):
        self.logout()
        Goal.query.delete()
        db.session.commit()


    def login(self):        
        self.test_client.post("/login/", data={"email": setup.test_user_name, "password": setup.test_user_pass})

    def logout(self):
        self.test_client.post("/logout/")

    def test_create(self):
        # Requires login:
        res = self.test_client.post("/goals/create/", data=self.new_goal)
        setup.assertRequiresLogin(self, res)

        self.login()

        ## Test that it rejects bad inputs
        bad_goal = self.new_goal.copy()
        bad_goal['name'] = None
        res = self.test_client.post("/goals/create/", data=bad_goal)
        setup.assertInvalid(self, res, "name")

        bad_goal['name'] = self.new_goal['name']
        bad_goal['prompt'] = "" 
        res = self.test_client.post("/goals/create/", data=bad_goal)

        setup.assertBadData(self, res, "Prompt must be between 0 and 255 characters")

        ## Test that it actually registers at all :-)
        res = self.test_client.post("/goals/create/", data=self.new_goal)
        setup.assertOk(self, res, 201)
        data = json.loads(res.data)
        self.assertIn('id', data)
        goal = Goal.pull_by_id(data['id'])
        self.assertIsNotNone(goal)
        for key, val in self.new_goal.iteritems():
            self.assertEqual(val, data[key])
            self.assertEqual(val, getattr(goal, key))

        ## Shouldn't be able to register something that already exists
        res = self.test_client.post("/goals/create/", data=self.new_goal)
        self.assertEqual(res.status_code, 409)
        data = json.loads(res.data)
        self.assertIn('detail', data)
        self.assertIn('Test goal already exists', data['detail'])

    def test_delete(self):
        # Requires login:
        res = self.test_client.post("/goals/delete/", 0)
        setup.assertRequiresLogin(self, res)

        self.login()
        new_goal = self.create_test_goal()

        res = self.test_client.post("/goals/delete/", data={'id': new_goal['id']})
        setup.assertOk(self, res, 204)

        res = self.test_client.post("/goals/delete/", data={'id': new_goal['id']})
        self.assertEqual(res.status_code, 404)
        data = json.loads(res.data)
        self.assertIn("detail", data)
        self.assertIn("does not exist", data['detail'])

        ## Need to somehow test out trying to delete someone *else*'s goal.

        

    def create_test_goal(self):
        res = self.test_client.post("/goals/create/", data=self.new_goal)
        setup.assertOk(self, res, 201)

        return json.loads(res.data)


        
        


