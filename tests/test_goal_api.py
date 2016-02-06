import setup
import unittest
from goly import app, db
from goly.models.user import User
from goly.models.goal import Goal
from sqlalchemy import func
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
        db.session.query(Goal).delete()
        db.session.commit()

    def tearDown(self):
        self.logout()
        db.session.query(Goal).delete()
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
        res = self.test_client.get("/goals/users/me/")
        setup.assertRequiresLogin(self, res)
        
        # Empty if user has no goals
        self.login()
        res = self.test_client.get("/goals/users/me/")
        setup.assertOk(self, res)
        data = json.loads(res.data)
        self.assertIn("goals", data)
        self.assertEqual(len(data['goals']), 0)
        
        ## Shows all (public and private) goals for current user
        setup.create_test_goals()
        res = self.test_client.get("/goals/users/me/")
        setup.assertOk(self, res)
        data = json.loads(res.data)
        self.assertIn("goals", data)
        self.assertEqual(len(data['goals']), 20) # default count is 20
        name_appendix = ord('a')
        for goal in data['goals']:
            self.assertFalse(goal['public']) # by default they're all private
            self.assertTrue(goal['active']) # by default they're all active
            self.assertEqual(goal['name'], "test goal " + chr(name_appendix)) # by default sort by name ASC
            name_appendix = name_appendix + 1

        public_goals = db.session.query(Goal).order_by(func.rand()).limit(15)
        for goal in public_goals:
            goal.update({"public": True})

        res = self.test_client.get("/goals/users/me/")
        setup.assertOk(self, res)
        data = json.loads(res.data)
        self.assertIn("goals", data)
        self.assertEqual(len(data['goals']), 20) # default count is 20
        name_appendix = ord('a')
        is_public = False ## Test to make sure at least one is public
        is_private = False # ditto private
        for goal in data['goals']:
            if (goal['public']): is_public = True
            else: is_private = True
            self.assertTrue(goal['active']) # by default they're all active
            self.assertEqual(goal['name'], "test goal " + chr(name_appendix)) # by default sort by name ASC
            name_appendix = name_appendix + 1

        self.assertTrue(is_public)
        self.assertTrue(is_private)

        ## Count works
        res = self.test_client.get("/goals/users/me/?count=3")
        setup.assertOk(self, res)
        data = json.loads(res.data)
        self.assertIn("goals", data)
        self.assertEqual(len(data['goals']), 3) # default count is 20
        name_appendix = chr(ord('a') - 1)
        for goal in data['goals']:
            self.assertTrue(goal['active']) # by default they're all active
            new_appendix = goal['name'].replace("test goal ", "")
            self.assertTrue(ord(new_appendix) > ord(name_appendix))
            name_appendix = new_appendix

        
        ## Sort rejects invalid inputs
        res = self.test_client.get("/goals/users/me/?sort=banana")
        setup.assertBadData(self, res, "sort can only be one of")

        ## Sort works -- and it should always give active first, then inactive
        active_goals = db.session.query(Goal).order_by(func.rand()).limit(15)
        for goal in active_goals:
            goal.update({"active": False})

        res = self.test_client.get("/goals/users/me/?sort=created")
        setup.assertOk(self, res)
        data = json.loads(res.data)
        self.assertIn("goals", data)
        self.assertEqual(len(data['goals']), 20) # default count is 20
        is_active = False
        is_inactive = False
        test_created = str(datetime.datetime(1970, 1, 1, 0, 0, 0))
        for goal in data['goals']: 
            if (goal['active']):
                is_active = True
            if (not goal['active']):
                if (not is_inactive):
                    test_created = str(datetime.datetime(1970, 1, 1, 0, 0, 0)) # reset the sort on the first inactive goal
                is_inactive = True
            self.assertTrue(goal['created'] > test_created)
            test_created = goal['created']
        self.assertTrue(is_active)
        self.assertTrue(is_inactive)
        
        ## Sort order rejects invalid inputs
        res = self.test_client.get("/goals/users/me/?sort_order=banana")
        setup.assertBadData(self, res, "sort_order must be either")

        ## Sort_order works
        res = self.test_client.get("/goals/users/me/?sort=created&sort_order=desc")
        setup.assertOk(self, res)
        data = json.loads(res.data)
        self.assertIn("goals", data)
        self.assertEqual(len(data['goals']), 20) # default count is 20
        is_active = False
        is_inactive = False
        test_created = str(datetime.datetime(2100, 1, 1, 0, 0, 0))
        for goal in data['goals']: 
            if (goal['active']):
                is_active = True
            if (not goal['active']):
                if (not is_inactive):
                    test_created = str(datetime.datetime(2100, 1, 1, 0, 0, 0)) # reset the sort on the first inactive goal
                is_inactive = True
            self.assertTrue(goal['created'] < test_created)
            test_created = goal['created']
        self.assertTrue(is_active)
        self.assertTrue(is_inactive)
        
        ## Offset works
        min_name = db.session.query(Goal).filter_by(active=True).order_by(Goal.name).first().name
        res = self.test_client.get("/goals/users/me/?offset=1")
        setup.assertOk(self, res)
        data = json.loads(res.data)
        self.assertIn("goals", data)
        self.assertEqual(len(data['goals']), 20) # default count is 20
        self.assertTrue(data['goals'][0]['name'] > min_name)

        
        ## Count, sort, sort order, and offset all work together
        max_created = db.session.query(Goal).filter_by(active=True).order_by(Goal.created.desc()).first().created
        res = self.test_client.get("/goals/users/me/?offset=1&count=1&sort=created&sort_order=desc")
        setup.assertOk(self, res)
        data = json.loads(res.data)
        self.assertIn("goals", data)
        self.assertEqual(len(data['goals']), 1)
        self.assertTrue(data['goals'][0]['created'] < str(max_created))

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
        
        ## Shows only public goals even for current user
        setup.create_test_goals()
        res = self.test_client.get("/goals/users/" + user_id + "/")
        setup.assertOk(self, res)
        data = json.loads(res.data)
        self.assertIn("goals", data)
        self.assertEqual(len(data['goals']), 0) # No public goals
        
        public_goals = db.session.query(Goal).all()
        for goal in public_goals:
            goal.update({"public": True})

        res = self.test_client.get("/goals/users/" + user_id + "/")
        setup.assertOk(self, res)
        data = json.loads(res.data)
        self.assertIn("goals", data)
        self.assertEqual(len(data['goals']), 20) # default count is 20
        name_appendix = ord('a')
        is_public = False ## Test to make sure at least one is public
        is_private = False # none should be private
        for goal in data['goals']:
            if (goal['public']): is_public = True
            else: is_private = True
            self.assertTrue(goal['active']) # by default they're all active
            self.assertEqual(goal['name'], "test goal " + chr(name_appendix)) # by default sort by name ASC
            name_appendix = name_appendix + 1

        self.assertTrue(is_public)
        self.assertFalse(is_private)
        
        ## Only shows public goals for other users
        self.logout()
        self.login_other_user()
        res = self.test_client.get("/goals/users/" + user_id + "/")
        setup.assertOk(self, res)
        data = json.loads(res.data)
        self.assertIn("goals", data)
        self.assertEqual(len(data['goals']), 20) # default count is 20
        name_appendix = ord('a')
        is_public = False ## Test to make sure at least one is public
        is_private = False # none should be private
        for goal in data['goals']:
            if (goal['public']): is_public = True
            else: is_private = True
            self.assertTrue(goal['active']) # by default they're all active
            self.assertEqual(goal['name'], "test goal " + chr(name_appendix)) # by default sort by name ASC
            name_appendix = name_appendix + 1

        self.assertTrue(is_public)
        self.assertFalse(is_private)

        public_goals = db.session.query(Goal).all()
        for goal in public_goals:
            goal.update({"public": False})

        res = self.test_client.get("/goals/users/" + user_id + "/")
        setup.assertOk(self, res)
        data = json.loads(res.data)
        self.assertIn("goals", data)
        self.assertEqual(len(data['goals']), 0) # No public goals
            
        ## Count works
        public_goals = db.session.query(Goal).all()
        for goal in public_goals:
            goal.update({"public": True})

        res = self.test_client.get("/goals/users/" + user_id + "/?count=3")
        setup.assertOk(self, res)
        data = json.loads(res.data)
        self.assertIn("goals", data)
        self.assertEqual(len(data['goals']), 3) # default count is 20
        name_appendix = chr(ord('a') - 1)
        for goal in data['goals']:
            self.assertTrue(goal['active']) # by default they're all active
            new_appendix = goal['name'].replace("test goal ", "")
            self.assertTrue(ord(new_appendix) > ord(name_appendix))
            name_appendix = new_appendix
        
        ## Sort rejects invalid inputs
        res = self.test_client.get("/goals/users/" + user_id + "/?sort=banana")
        setup.assertBadData(self, res, "sort can only be one of")

        ## Sort works
        ## Sort works -- and it should always give active first, then inactive
        active_goals = db.session.query(Goal).order_by(func.rand()).limit(15)
        for goal in active_goals:
            goal.update({"active": False})

        res = self.test_client.get("/goals/users/" + user_id + "/?sort=created")
        setup.assertOk(self, res)
        data = json.loads(res.data)
        self.assertIn("goals", data)
        self.assertEqual(len(data['goals']), 20) # default count is 20
        is_active = False
        is_inactive = False
        test_created = str(datetime.datetime(1970, 1, 1, 0, 0, 0))
        for goal in data['goals']: 
            if (goal['active']):
                is_active = True
            if (not goal['active']):
                if (not is_inactive):
                    test_created = str(datetime.datetime(1970, 1, 1, 0, 0, 0)) # reset the sort on the first inactive goal
                is_inactive = True
            self.assertTrue(goal['created'] > test_created)
            test_created = goal['created']
        self.assertTrue(is_active)
        self.assertTrue(is_inactive)
        
        ## Sort order rejects invalid inputs
        res = self.test_client.get("/goals/users/" + user_id + "/?sort_order=banana")
        setup.assertBadData(self, res, "sort_order must be either")

        ## Sort_order works
        res = self.test_client.get("/goals/users/" + user_id + "/?sort=created&sort_order=desc")
        setup.assertOk(self, res)
        data = json.loads(res.data)
        self.assertIn("goals", data)
        self.assertEqual(len(data['goals']), 20) # default count is 20
        is_active = False
        is_inactive = False
        test_created = str(datetime.datetime(2100, 1, 1, 0, 0, 0))
        for goal in data['goals']: 
            if (goal['active']):
                is_active = True
            if (not goal['active']):
                if (not is_inactive):
                    test_created = str(datetime.datetime(2100, 1, 1, 0, 0, 0)) # reset the sort on the first inactive goal
                is_inactive = True
            self.assertTrue(goal['created'] < test_created)
            test_created = goal['created']
        self.assertTrue(is_active)
        self.assertTrue(is_inactive)
        
        ## Offset works
        min_name = db.session.query(Goal).filter_by(active=True).order_by(Goal.name).first().name
        res = self.test_client.get("/goals/users/" + user_id + "/?offset=1")
        setup.assertOk(self, res)
        data = json.loads(res.data)
        self.assertIn("goals", data)
        self.assertEqual(len(data['goals']), 20) # default count is 20
        self.assertTrue(data['goals'][0]['name'] > min_name)
        
        ## Count, sort, sort order, and offset all work together
        max_created = db.session.query(Goal).filter_by(active=True).order_by(Goal.created.desc()).first().created
        res = self.test_client.get("/goals/users/" + user_id + "/?offset=1&count=1&sort=created&sort_order=desc")
        setup.assertOk(self, res)
        data = json.loads(res.data)
        self.assertIn("goals", data)
        self.assertEqual(len(data['goals']), 1)
        self.assertTrue(data['goals'][0]['created'] < str(max_created))


    def create_test_goal(self):
        res = self.test_client.post("/goals/create/", data=self.new_goal)
        setup.assertOk(self, res, 201)

        return json.loads(res.data)


if __name__ == '__main__':
    unittest.main()