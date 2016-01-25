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
        res = self.test_client.post("/login/", data={"email": setup.test_user_name, "password": setup.test_user_pass})
        setup.assertOk(self, res, 201)

    def logout(self):
        res = self.test_client.post("/logout/")
        setup.assertOk(self, res, 204)

    def login_other_user(self):
        setup.create_other_user()
        res = self.test_client.post("/login/", data={"email": setup.other_user_name, "password": setup.other_user_pass})
        setup.assertOk(self, res, 201)

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
        res = self.test_client.post("/goals/delete/", data={'id': 0})
        setup.assertRequiresLogin(self, res)

        self.login()

        ## Validates form:
        res = self.test_client.post("/goals/delete/", data={'foo': 'bar'})
        setup.assertInvalid(self, res, "id")

        ## works at all
        new_goal = self.create_test_goal()

        res = self.test_client.post("/goals/delete/", data={'id': new_goal['id']})
        setup.assertOk(self, res, 204)

        ## 404s
        res = self.test_client.post("/goals/delete/", data={'id': new_goal['id']})
        setup.assert404(self, res)

        ## Can't someone *else*'s goal.
        new_goal = self.create_test_goal()
        self.logout()

        self.login_other_user()
        res = self.test_client.post("/goals/delete/", data={'id': new_goal['id']})
        setup.assertInvalidCredentials(self, res)

    def test_update(self):
        ## Requires login
        res = self.test_client.post("/goals/update/", data={'id': 0})
        setup.assertRequiresLogin(self, res)

        ## Validates form
        self.login()
        res = self.test_client.post("/goals/update/", data={'favorite_muppet': 'kermit'})
        setup.assertInvalid(self, res, 'id')        
        
        ## 404's
        res = self.test_client.post("/goals/update/", data={'id': 0, 'name': 'test goal 2.0'})
        setup.assert404(self, res)

        ## Actually works
        goal = self.create_test_goal()
        data = {'id': goal['id']}
        data['name'] = "Test Goal 2.0"
        data['prompt'] = "Guess how many eggs I had for breakfast today!"
        data['frequency'] = "monthly"
        data['target'] = 100
        data['input_type'] = "binary"
        data['active'] = False
        data['public'] = True
        
        res = self.test_client.post("/goals/update/", data=data)
        setup.assertOk(self, res, 200)

        updated_goal = Goal.pull_by_id(goal['id'])
        for key, val in data.iteritems():
            self.assertEqual(getattr(updated_goal, key), val)

        ## If any part is invalid, no part should go through
        bad_data = {'id': goal['id']}
        bad_data['name'] = "Test Goal 3.0"
        bad_data['prompt'] = "How many jars of sand did you collect?"
        bad_data['frequency'] = "daily"
        bad_data['target'] = 1000
        bad_data['input_type'] = "numeric"
        bad_data['active'] = True
        bad_data['public'] = "banana"

        res = self.test_client.post("/goals/update/", data=bad_data)
        setup.assertBadData(self, res, "Public must be a boolean")
        updated_goal = Goal.pull_by_id(goal['id'])
        for key, val in data.iteritems():
            self.assertEqual(getattr(updated_goal, key), val)

        
        ## Can't update someone else's goal
        self.logout()
        self.login_other_user()
        res = self.test_client.post("/goals/update/", data=bad_data) ## using bad_data here ensures we don't update
        setup.assertInvalidCredentials(self, res)
        
    def test_get(self):
        ## Requires login
        res = self.test_client.get("/goals/0/")
        setup.assertRequiresLogin(self, res)

        ## 404s
        self.login()
        res = self.test_client.get("/goals/0/")
        setup.assert404(self, res)        
        
        ## Can access own private goals
        goal = self.create_test_goal()
        res = self.test_client.get('/goals/' + str(goal['id']) + '/')
        setup.assertOk(self, res, 200)
        self.assertEqual(json.loads(res.data), goal)

        ## Cannot access other's private goals
        self.logout()
        self.login_other_user()
        res = self.test_client.get('/goals/' + str(goal['id']) + '/')
        setup.assertInvalidCredentials(self, res)
        
        ## Can access own public goals
        self.logout()
        self.login()
        res = self.test_client.post("/goals/update/", data={'id': goal['id'], 'public': True})
        setup.assertOk(self, res)
        res = self.test_client.get('/goals/' + str(goal['id']) + '/')
        setup.assertOk(self, res, 200)
        goal['public'] = True
        self.assertEqual(json.loads(res.data), goal)
        
        ## Can access others' public goals
        self.logout()
        self.login_other_user()
        res = self.test_client.get('/goals/' + str(goal['id']) + '/')
        setup.assertOk(self, res, 200)
        self.assertEqual(json.loads(res.data), goal)

    def test_get_my_goals(self):
        ## Requires login
        res = self.test_client.get("/goals/users/me")
        setup.assertRequiresLogin(self, res)
        
        # Empty if user has no goals
        self.login()
        res = self.test_client.get("/goals/users/me")
        setup.assertOk(self, res)
        data = json.loads(res.data)
        self.assertIn("goals", data)
        self.assertEqual(len(data['goals']), 0)
        
        ## Shows all (public and private) goals for current user
        
        ## Count works
        
        ## Sort rejects invalid inputs

        ## Sort works
        
        ## Sort order rejects invalid inputs

        ## Sort_order works
        
        ## Offset works
        
        ## Count, sort, sort order, and offset all work together


    def test_index(self):
        ## Requires login
        res = self.test_client.get("/goals/users/0/")
        setup.assertRequiresLogin(self, res)
        
        ## 404s on bum user
        self.login()
        res = self.test_client.get("/goals/users/0/")
        setup.assert404(self, res)
        
        # Empty if user has no goals
        user_id = str(json.loads(self.test_client.get("/users/me/").data)['id'])
        res = self.test_client.get("/goals/users/" + user_id +"/")
        setup.assertOk(self, res)
        data = json.loads(res.data)
        self.assertIn("goals", data)
        self.assertEqual(len(data['goals']), 0)
        
        ## Only shows public goals for other users
        
        ## Shows only public goals even for current user
        
        ## Count works
        
        ## Sort rejects invalid inputs

        ## Sort works
        
        ## Sort order rejects invalid inputs

        ## Sort_order works
        
        ## Offset works
        
        ## Count, sort, sort order, and offset all work together
        


        

    def create_test_goal(self):
        res = self.test_client.post("/goals/create/", data=self.new_goal)
        setup.assertOk(self, res, 201)

        return json.loads(res.data)


        
        


