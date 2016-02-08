import setup
import unittest
from goly.models.goal import Goal
from goly.models.user import User
from goly.models.frequency import Frequency
import json
import goly.errors
from goly import db

class TestGoal(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.test_user = setup.create_test_user()

    @classmethod
    def tearDownClass(self):
        User.query.delete()
        db.session.commit()

    def setUp(self):
        Goal.query.delete()
        db.session.commit()

    def tearDown(self):
        Goal.query.delete()
        db.session.commit()

    def create_test_goal(self):
        goal = Goal(self.test_user, "test goal", "is this goal a test?", "weekly", 10, "binary", "daily")
        goal.persist()

        return goal

    def test_init(self):
        ## Test that all of the validators work!
        fake_user = User("notreal", "notreal", "notreal", "notreal")
        with self.assertRaisesRegexp(AssertionError, "user does not exist"):
            goal = Goal(fake_user, "test name", "test prompt", "weekly", 10, "binary", "daily")

        with self.assertRaisesRegexp(AssertionError, "user must be a User"):
            goal = Goal("Jimmy", "test", "test prompt", "weekly", 10, "binary", "daily")

        with self.assertRaisesRegexp(AssertionError, "Name must be between 0 and 50"):
            goal = Goal(self.test_user, " ", "test prompt", "weekly", 10, "binary", "daily")

        with self.assertRaisesRegexp(AssertionError, "Name must be between 0 and 50"):
            goal = Goal(self.test_user, "a" * 51, "test prompt", "weekly", 10, "binary", "daily")        

        with self.assertRaisesRegexp(AssertionError, "Prompt must be between 0 and 255"):
            goal = Goal(self.test_user, "test", " ", "weekly", 10, "binary", "daily")

        with self.assertRaisesRegexp(AssertionError, "Prompt must be between 0 and 255"):
            goal = Goal(self.test_user, "test", "a" * 256, "weekly", 10, "binary", "daily")        

        with self.assertRaisesRegexp(AssertionError, "frequency must be one of "):
            goal = Goal(self.test_user, "test", "test prompt", "not-an-option", 10, "binary", "daily")        

        with self.assertRaisesRegexp(AssertionError, "Target must be an integer"):
            goal = Goal(self.test_user, "test", "test prompt", "weekly", "banana", "binary", "daily")        

        with self.assertRaisesRegexp(AssertionError, "Input type must be binary or numeric"):
            goal = Goal(self.test_user, "test", "test prompt", "weekly", 10, "banana", "daily")        

        with self.assertRaisesRegexp(AssertionError, "check_in_frequency must be one of"):
            goal = Goal(self.test_user, "test", "test prompt", "weekly", 10, "numeric", "only on fudge sundaes")        

        with self.assertRaisesRegexp(AssertionError, "Check-in frequency must conform to frequency"):
            goal = Goal(self.test_user, "test", "test prompt", "weekly", 10, "numeric", "monthly")        

        goal = Goal(self.test_user, "test", "test prompt", "weekly", "10", "binary", "daily")
        self.assertIsInstance(goal, Goal)
        self.assertTrue(goal.active)
        self.assertFalse(goal.public)

        with self.assertRaisesRegexp(AssertionError, "Active must be a boolean"):
            goal.active = "fish"

        with self.assertRaisesRegexp(AssertionError, "Public must be a boolean"):
            goal.public = "filet"

    def test_persist(self): ## This sorta also tests pull by ID and exists(), fwiw
        goal = self.create_test_goal() ## Calls persist
        self.assertTrue(goal.exists())

        check = Goal.pull_by_id(goal.id)
        self.assertEqual(goal, check)

        with self.assertRaisesRegexp(goly.errors.ResourceAlreadyExistsError, "Unable to create goal"):
            goal.persist()

    def test_destroy(self):
        goal = self.create_test_goal()
        self.assertTrue(goal.exists())

        goal.destroy()
        self.assertFalse(goal.exists())     

    def test_update(self):
        goal = self.create_test_goal()

        with self.assertRaisesRegexp(goly.errors.ResourceAlreadyExistsError, "Unable to create goal"):
            goal.update({"name": goal.name})

        data = {
            "name": "New test name",
            "prompt": "New test prompt",
            "frequency": "yearly", 
            "check_in_frequency": "quarterly",
            "target": 100,
            "input_type": "numeric",
            "active": False,
            "public": True
        }

        goal.update(data)

        for attr, name in data.iteritems():
            if (attr in['check_in_frequency', 'frequency']):
                self.assertEqual(Frequency.get_name_by_id(getattr(goal, attr)), data[attr])
            else: self.assertEqual(getattr(goal, attr), data[attr])


        check = Goal.pull_by_id(goal.get_id()) ## make sure these persisted

        for attr, name in data.iteritems():
            if (attr in['check_in_frequency', 'frequency']):
                self.assertEqual(Frequency.get_name_by_id(getattr(goal, attr)), data[attr])
            else: self.assertEqual(getattr(goal, attr), data[attr])

        with self.assertRaisesRegexp(AssertionError, "Name must be between 0 and 50"):
            goal.update({"name": " "})

        with self.assertRaisesRegexp(AssertionError, "Name must be between 0 and 50"):
            goal.update({"name": "a" * 51})        

        with self.assertRaisesRegexp(AssertionError, "Prompt must be between 0 and 255"):
            goal.update({"prompt": " "})

        with self.assertRaisesRegexp(AssertionError, "Prompt must be between 0 and 255"):
            goal.update({"prompt": "a" * 256})

        with self.assertRaisesRegexp(AssertionError, "frequency must be one of "):
            goal.update({"frequency": "not-an-option"})

        with self.assertRaisesRegexp(AssertionError, "Target must be an integer"):
            goal.update({"target": "banana"})

        with self.assertRaisesRegexp(AssertionError, "Input type must be binary or numeric"):
            goal.update({"input_type": "pineapple"})

        with self.assertRaisesRegexp(AssertionError, "Active must be a boolean"):
            goal.update({'active': "fish"})

        with self.assertRaisesRegexp(AssertionError, "Public must be a boolean"):
            goal.update({"public": "filet"})

        with self.assertRaisesRegexp(AssertionError, "check_in_frequency must be one of"):
            goal.update({"check_in_frequency": "whenever I feel like it, gosh"})
        
        with self.assertRaisesRegexp(AssertionError, "Check-in frequency must conform"):
            goal.update({"check_in_frequency": "weekly"})

if (__name__ == '__main__'):
    unittest.main()