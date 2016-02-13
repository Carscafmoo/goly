import setup
import unittest
from goly.models.check_in import CheckIn
from goly.models.timeframe import Timeframe
from goly.models.goal import Goal
from goly import db
import datetime

class TestCheckIn(unittest.TestCase):
    test_tf = Timeframe("daily", datetime.datetime(2016, 1, 1))
    test_user = setup.create_test_user()
    test_binary_goal = Goal(test_user, "test binary goal", "is this goal a test?", "weekly", 10, "binary", "daily")
    test_numeric_goal = Goal(test_user, "test numeric goal", "is this goal a test?", "weekly", 10, "numeric", "daily")
    
    test_binary_goal.persist()
    test_numeric_goal.persist()

    @classmethod
    def startUpClass(self):
        Goal.query.delete()
        db.session.commit()

    @classmethod
    def tearDownClass(self):
        CheckIn.query.delete()
        Goal.query.delete()
        db.session.commit()

    def startUp(self):
        CheckIn.query.delete()

    def tearDown(self):
        CheckIn.query.delete()

    def test_init(self):
        ## Should fail if bogus goal is specified
        with self.assertRaisesRegexp(AssertionError, "Passed goal must be a goal object"):
            ci = CheckIn("bogus", self.test_tf, 1)

        ## Should fail if not a timeframe
        with self.assertRaisesRegexp(AssertionError, "Passed timeframe must be a timeframe object"):
            ci = CheckIn(self.test_numeric_goal, "bogus", 1)        

        ## Should fail if timeframe doesn't conform:
        with self.assertRaisesRegexp(AssertionError, "Passed timeframe frequency must match"):
            ci = CheckIn(self.test_numeric_goal, Timeframe("weekly", datetime.datetime(2016,2,7)), 1)                

        ## Should fail if numeric and a boolean is passed
        with self.assertRaisesRegexp(AssertionError, "Value must be numeric"):
            ci = CheckIn(self.test_numeric_goal, self.test_tf, "orange you glad I didn't say banana?'")

        ## Should fail if binary and a number is passed
        with self.assertRaisesRegexp(AssertionError, "Value must be a boolean"):
            ci = CheckIn(self.test_binary_goal, self.test_tf, 30)

        ## Should actually work if everything is provided correctly
        ci = CheckIn(self.test_numeric_goal, self.test_tf, 30)
        self.assertEqual(ci.goal_obj, self.test_numeric_goal)
        self.assertEqual(ci.goal, self.test_numeric_goal.get_id())
        self.assertEqual(ci.timeframe_obj, self.test_tf)
        self.assertEqual(ci.timeframe, self.test_tf.get_id())
        self.assertEqual(ci.value, 30)

        ci = CheckIn(self.test_binary_goal, self.test_tf, True)
        self.assertEqual(ci.goal_obj, self.test_binary_goal)
        self.assertEqual(ci.goal, self.test_binary_goal.get_id())
        self.assertEqual(ci.timeframe_obj, self.test_tf)
        self.assertEqual(ci.timeframe, self.test_tf.get_id())
        self.assertEqual(ci.value, 1)

    def test_persist(self): ## also tests exists, really -- and pull_by_id
        ci = self.get_test_check_in()
        self.assertFalse(ci.exists())
        ci.persist()
        self.assertTrue(ci.exists())
        self.assertIsNotNone(ci.get_id())
        self.assertEqual(ci.to_dict(), CheckIn.pull_by_id(ci.get_id()).to_dict())

        ## now if you overwrite that it should still work.
        ci = CheckIn(self.test_numeric_goal, self.test_tf, 60)
        self.assertTrue(ci.exists())
        ci.persist()        
        test_ci = CheckIn.pull_by_id(ci.get_id())
        self.assertEqual(ci.to_dict(), test_ci.to_dict())
        self.assertEqual(test_ci.value, 60)

    def test_pull_by_goal_timeframe(self):
        ci = CheckIn.pull_by_goal_timeframe(self.test_numeric_goal.get_id(), self.test_tf.get_id())
        self.assertIsNone(ci)
        ci = self.get_test_check_in()
        ci.persist()
        test_ci = CheckIn.pull_by_goal_timeframe(self.test_numeric_goal.get_id(), self.test_tf.get_id())
        self.assertEqual(ci.to_dict(), test_ci.to_dict())

    def test_destroy(self):
        ci = self.get_test_check_in()
        ci.persist()
        self.assertTrue(ci.exists())
        ci.destroy()
        self.assertFalse(ci.exists())

    def test_pull_by_goal_start_end(self):
        ci = self.get_test_check_in()
        ci.persist()
        for x in range(0, 7):
            tf = ci.timeframe_obj
            new_tf = Timeframe(tf.frequency_name, tf.start + datetime.timedelta(1))
            ci = CheckIn(ci.goal_obj, new_tf, x)
            ci.persist() 
            

        cis = CheckIn.pull_by_goal_start_end(ci.goal, datetime.datetime(2016, 1, 1), datetime.datetime(2016, 1, 8))
        self.assertEqual(len(cis), 7)

    def test_pull_by_goal_timeframes(self):
        ci = self.get_test_check_in()
        timeframes = [ci.timeframe]
        ci.persist()
        for x in range(0, 7):
            tf = ci.timeframe_obj
            new_tf = Timeframe(tf.frequency_name, tf.start + datetime.timedelta(1))
            timeframes.append(new_tf.get_id())
            ci = CheckIn(ci.goal_obj, new_tf, x)
            ci.persist() 
            

        cis = CheckIn.pull_by_goal_timeframes(ci.goal, timeframes)
        self.assertEqual(len(cis), 8)

    



        


    def get_test_check_in(self):
        return CheckIn(self.test_numeric_goal, self.test_tf, 30)


if __name__ == '__main__':
    unittest.main()

