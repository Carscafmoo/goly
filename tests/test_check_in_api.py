import setup
import unittest
from goly import app, db
from goly.models.user import User
from goly.models.goal import Goal
from goly.models.timeframe import Timeframe
from goly.models.check_in import CheckIn
import json
import datetime

class TestCheckInApi(unittest.TestCase):
    test_client = setup.test_client
   
    @classmethod
    def setUpClass(self):
        User.query.delete()
        db.session.commit()
        

    @classmethod
    def tearDownClass(self):
        User.query.delete()
        db.session.commit()

    def setUp(self):
        db.session.query(CheckIn).delete()
        db.session.query(Goal).delete()
        db.session.commit()

    def tearDown(self):
        self.logout()
        db.session.query(CheckIn).delete()
        db.session.query(Goal).delete()
        db.session.commit()

    def login(self):        
        return setup.assertOk(self, setup.login_test_user(), 201)

    def logout(self):
        return setup.assertOk(self, setup.logout(), 204)

    def login_other_user(self):
        return setup.assertOk(self, setup.login_other_user(), 201)

    def test_check_in(self):
        tc = self.test_client

        # Requires Login:
        res = tc.post("/goals/1/check-ins/", data={"value": 1})
        setup.assertRequiresLogin(self, res)

        ## Requires "value"
        self.login()
        res = tc.post("/goals/1/check-ins/", data={"not-value": 1})
        setup.assertInvalid(self, res, "value")

        ## Must be a goal that exists
        res = tc.post("/goals/0/check-ins/", data={"value": 1})
        setup.assert404(self, res)        
        
        ## User must own the goal in question
        numeric_goal = self.create_test_numeric_goal()
        numeric_goal_id = str(numeric_goal.get_id()) ## You have to do this before you log out, for some reason?
        binary_goal = self.create_test_binary_goal()
        binary_goal_id = str(binary_goal.get_id())
        
        self.logout()
        self.login_other_user()
        res = tc.post("/goals/" + numeric_goal_id + "/check-ins/", data={"value": 1})
        setup.assertInvalidCredentials(self, res)
        
        ## Check-in must conform (true / false vs. numeric)
        self.logout()
        self.login()
        res = tc.post("/goals/" + numeric_goal_id + "/check-ins/", data={"value": "true"})
        setup.assertBadData(self, res, "Value must be numeric")

        res = tc.post("/goals/" + binary_goal_id + "/check-ins/", data={"value": 10})
        setup.assertBadData(self, res, "Value must be a boolean")        

        ## Check-in is returned with 201 if no timeframe is given, returning current timeframe (both numeric & binary)
        res = tc.post("/goals/" + numeric_goal_id + "/check-ins/", data={"value": 1})
        setup.assertOk(self, res, 201)
        data = json.loads(res.data)
        self.assertIn("id", data)
        self.assertEqual(str(data['goal']), numeric_goal_id)
        self.assertEqual(data['value'], 1)
        self.assertEqual(data['timeframe'], Timeframe.get_current_timeframe('daily').to_dict())
        self.assertEqual(CheckIn.pull_by_id(data['id']).to_dict(), data)

        res = tc.post("/goals/" + binary_goal_id + "/check-ins/", data={"value": True})
        setup.assertOk(self, res, 201)
        data = json.loads(res.data)
        self.assertIn("id", data)
        self.assertEqual(str(data['goal']), binary_goal_id)
        self.assertEqual(data['value'], 1)
        self.assertEqual(data['timeframe'], Timeframe.get_current_timeframe('daily').to_dict())
        self.assertEqual(CheckIn.pull_by_id(data['id']).to_dict(), data)

        ## An updated check-in is returned with 200 if no timeframe is given, returning current timeframe
        res = tc.post("/goals/" + numeric_goal_id + "/check-ins/", data={"value": 3})
        setup.assertOk(self, res, 200)
        data = json.loads(res.data)
        self.assertIn("id", data)
        self.assertEqual(str(data['goal']), numeric_goal_id)
        self.assertEqual(data['value'], 3)
        self.assertEqual(data['timeframe'], Timeframe.get_current_timeframe('daily').to_dict())
        self.assertEqual(CheckIn.pull_by_id(data['id']).to_dict(), data)

        ## Check-in is returned with 201 if timeframe ID is given, returning correct timeframe
        tf = Timeframe.get_timeframe("daily", datetime.datetime(2016, 1, 1))
        res = tc.post("/goals/" + numeric_goal_id + "/check-ins/", data={"value": 1, "timeframe": tf.get_id()})
        setup.assertOk(self, res, 201)
        data = json.loads(res.data)
        self.assertIn("id", data)
        self.assertEqual(str(data['goal']), numeric_goal_id)
        self.assertEqual(data['value'], 1)
        self.assertEqual(data['timeframe'], tf.to_dict())
        self.assertEqual(CheckIn.pull_by_id(data['id']).to_dict(), data)
        
        ## Updated check-in is returned with 200 if Timeframe ID is given, returning correct timeframe
        res = tc.post("/goals/" + numeric_goal_id + "/check-ins/", data={"value": 3, "timeframe": tf.get_id()})
        setup.assertOk(self, res, 200)
        data = json.loads(res.data)
        self.assertIn("id", data)
        self.assertEqual(str(data['goal']), numeric_goal_id)
        self.assertEqual(data['value'], 3)
        self.assertEqual(data['timeframe'], tf.to_dict())
        self.assertEqual(CheckIn.pull_by_id(data['id']).to_dict(), data)

    def test_get_current(self):
        tc = self.test_client
        ## Login required
        setup.assertRequiresLogin(self, tc.get("/goals/0/check-ins/current/"))

        ## Goal exists
        self.login()
        setup.assert404(self, tc.get("/goals/0/check-ins/current/"))
        
        ## user is goal owner
        goal = self.create_test_numeric_goal()
        goal_id = str(goal.get_id())
        self.logout()
        self.login_other_user()
        setup.assertInvalidCredentials(self, tc.get("/goals/" + goal_id + "/check-ins/current/"))
        
        ## Check in must exist
        self.logout()
        self.login()
        setup.assert404(self, tc.get("/goals/" + goal_id + "/check-ins/current/"))

        ## Returns correctly
        ci = CheckIn(goal, Timeframe.get_current_timeframe(goal.check_in_frequency_name), 1)
        ci.persist()
        res = tc.get("/goals/" + goal_id + "/check-ins/current/")
        setup.assertOk(self, res, 200)
        self.assertEqual(json.loads(res.data), ci.to_dict())
        
    def test_get(self):
        tc = self.test_client
        ## Login required
        setup.assertRequiresLogin(self, tc.get("/goals/0/check-ins/0/"))

        ## Goal exists
        self.login()
        setup.assert404(self, tc.get("/goals/0/check-ins/0/"))
        
        ## user is goal owner
        goal = self.create_test_numeric_goal()
        goal_id = str(goal.get_id())
        self.logout()
        self.login_other_user()
        setup.assertInvalidCredentials(self, tc.get("/goals/" + goal_id + "/check-ins/0/"))
        
        ## Check in must exist
        self.logout()
        self.login()
        setup.assert404(self, tc.get("/goals/" + goal_id + "/check-ins/0/"))

        ## Returns correctly
        ci = CheckIn(goal, Timeframe.get_current_timeframe(goal.check_in_frequency_name), 1)
        ci.persist()
        tfid = str(ci.timeframe)
        res = tc.get("/goals/" + goal_id + "/check-ins/" + tfid + "/")
        setup.assertOk(self, res, 200)
        self.assertEqual(json.loads(res.data), ci.to_dict())

    def test_get_by_time(self):
        tc = self.test_client
        
        ## Login required
        setup.assertRequiresLogin(self, tc.get("/goals/0/check-ins/"))
        
        ## Goal must exist
        self.login()
        setup.assert404(self, tc.get("/goals/0/check-ins/"))
        
        ## User is the goal's owner
        goal = self.create_test_numeric_goal()
        goal_id = str(goal.get_id())
        self.logout()
        self.login_other_user()
        setup.assertInvalidCredentials(self, tc.get("/goals/" + goal_id + "/check-ins/"))
        
        ## Start and end are present
        self.logout()
        self.login()
        setup.assertBadData(self, tc.get("/goals/" + goal_id + "/check-ins/"), "start and end")
        setup.assertBadData(self, tc.get("/goals/" + goal_id + "/check-ins/?start=banana"), "start and end")
        setup.assertBadData(self, tc.get("/goals/" + goal_id + "/check-ins/?end=banana"), "start and end")
        
        ## Start and end in format YYYY-MM-DD HH:mm:ss
        res = tc.get("/goals/" + goal_id + "/check-ins/?start=2016-01-01 10:00:00&end=banana")
        setup.assertBadData(self, res, "'banana' does not match format")
        res = tc.get("/goals/" + goal_id + "/check-ins/?start=strawberry&end=2016-01-01 10:00:00")
        setup.assertBadData(self, res, "'strawberry' does not match format")
        
        ## Returns empty for no check-ins
        res = tc.get("/goals/" + goal_id + "/check-ins/?start=2016-01-01 00:00:00&end=2016-01-08 00:00:00")
        setup.assertOk(self, res)
        data = json.loads(res.data)
        self.assertIn("check-ins", data)
        self.assertEqual(len(data['check-ins']), 0)
        
        ## Correctly returns multiple check-ins
        ci = CheckIn(goal, Timeframe(goal.check_in_frequency_name, datetime.datetime(2015, 12, 31)), 0)
        ci.persist()
        for x in range(0, 8): #one preceding and one postceding so we can make sure this limits the results
            tf = ci.timeframe_obj
            new_tf = Timeframe(tf.frequency_name, tf.start + datetime.timedelta(1))
            ci = CheckIn(ci.goal_obj, new_tf, x)
            ci.persist() 

        res = tc.get("/goals/" + goal_id + "/check-ins/?start=2016-01-01 00:00:00&end=2016-01-08 00:00:00")
        setup.assertOk(self, res)
        data = json.loads(res.data)
        self.assertIn("check-ins", data)
        self.assertEqual(len(data['check-ins']), 7)
        for index, check_in in enumerate(data['check-ins']):
            self.assertEqual(index, check_in['value'])


    def create_test_numeric_goal(self):
        goal = Goal(setup.get_test_user(), 
            "Test Numeric goal", 
            "How many goals have you created today?", 
            "weekly", 
            7, 
            "numeric", 
            "daily")

        goal.persist()

        return goal

    def create_test_binary_goal(self):
        goal = Goal(setup.get_test_user(), 
            "Test Binary goal", 
            "Have you created a goal today?", 
            "weekly", 
            7, 
            "binary", 
            "daily")

        goal.persist()

        return goal

if (__name__ == '__main__'):
    unittest.main()