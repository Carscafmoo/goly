import setup
import unittest
from goly.models.timeframe import Timeframe
from goly import db
import datetime
import dateutil.relativedelta

class TestTimeframe(unittest.TestCase):
    def startUp(self):
        Timeframe.query.delete()

    def tearDown(self):
        Timeframe.query.delete()

    def test_init(self):
        ## Should fail if bogus frequency is specified
        with self.assertRaisesRegexp(AssertionError, "Frequency must be one of"):
            tf = Timeframe("bogus", datetime.datetime.now())

        ## start date for daily should always be the start of a day
        with self.assertRaisesRegexp(AssertionError, "Timeframe must begin at midnight"):
            tf = Timeframe("daily", datetime.datetime(2016, 1, 1, 1, 1, 1))
        with self.assertRaisesRegexp(AssertionError, "Timeframe must begin at midnight"):
            tf = Timeframe("daily", datetime.datetime(2016, 1, 1, 1, 1))
        with self.assertRaisesRegexp(AssertionError, "Timeframe must begin at midnight"):
            tf = Timeframe("daily", datetime.datetime(2016, 1, 1, 1))
        tf = Timeframe("daily", datetime.datetime(2016, 1, 1))
        self.assertEqual(tf.end, datetime.datetime(2016, 1, 2))

        with self.assertRaisesRegexp(AssertionError, "Weekly timeframes must begin on Sunday"):
            tf = Timeframe("weekly", datetime.datetime(2016, 1, 1))

        ## start date for monthly should always be the start of a month
        with self.assertRaisesRegexp(AssertionError, "Monthly timeframes must begin on the first"):
            tf = Timeframe("monthly", datetime.datetime(2016, 1, 2))
        tf = Timeframe("monthly", datetime.datetime(2016, 1, 1))
        self.assertEqual(tf.end, datetime.datetime(2016, 2, 1))
        
        ## start date for quarterly should always be the start of a quarter
        with self.assertRaisesRegexp(AssertionError, "Quarterly timeframes must begin "):
            tf = Timeframe("quarterly", datetime.datetime(2016, 2, 1))
        tf = Timeframe("quarterly", datetime.datetime(2016, 1, 1))
        self.assertEqual(tf.end, datetime.datetime(2016, 4, 1))
    
        ## start date for yearly should always be the start of a year
        with self.assertRaisesRegexp(AssertionError, "Yearly timeframes must begin on"):
            tf = Timeframe("yearly", datetime.datetime(2016, 4, 1))
        tf = Timeframe("yearly", datetime.datetime(2016, 1, 1))
        self.assertEqual(tf.end, datetime.datetime(2017, 1, 1))

        ## Should create a weekly timeframe if everything's cool
        now = datetime.datetime(2016, 2, 7)
        tf = Timeframe("weekly", now)
        self.assertEqual(tf.start, now)
        self.assertEqual(tf.end, now + datetime.timedelta(7))
        self.assertEqual(tf.frequency_name, "weekly")
        self.assertIs(type(tf.frequency), long)

    def test__calculate_end(self):
        time = datetime.datetime(2016, 2, 29) ## pretty much as edge case as you can get?
        tf = Timeframe("daily", time)
        self.assertEqual(tf._calculate_end(), datetime.datetime(2016, 3, 1))

        tf.frequency_name = "weekly"
        self.assertEqual(tf._calculate_end(), datetime.datetime(2016, 3, 7))

        tf.frequency_name = "monthly" 
        self.assertEqual(tf._calculate_end(), datetime.datetime(2016, 3, 29))

        tf.frequency_name = "quarterly"
        self.assertEqual(tf._calculate_end(), datetime.datetime(2016, 5, 29))

        tf.frequency_name = "yearly"
        self.assertEqual(tf._calculate_end(), datetime.datetime(2017, 2, 28))

    def test_get_most_recent_week_start(self):
        ## Should work for all days of the week
        for x in range(0, 7):
            time = datetime.datetime(2016, 2, 7) ## known Sunday
            test_time = time + dateutil.relativedelta.relativedelta(days=x)
            self.assertEqual(time, Timeframe.get_most_recent_week_start(test_time))
        
        ## Should work around edge cases -- year and month breaks
        time = datetime.datetime(2016, 1, 1)
        self.assertEqual(datetime.datetime(2015, 12, 27), Timeframe.get_most_recent_week_start(time))

    def test_get_timeframe(self):
        ## Each test tests that it gets the correct start / endpoints, even if the time is the start point
        tf = Timeframe.get_timeframe("daily", datetime.datetime(2016, 1, 1))
        self.assertEqual(tf.start, datetime.datetime(2016, 1, 1))
        self.assertEqual(tf.end, datetime.datetime(2016, 1, 2))
        new_tf = Timeframe.get_timeframe("daily", datetime.datetime(2016, 1, 1, 23, 59, 59, 99999))
        self.assertEqual(new_tf.to_dict(), tf.to_dict())

        tf = Timeframe.get_timeframe("weekly", datetime.datetime(2016, 2, 7))
        self.assertEqual(tf.start, datetime.datetime(2016, 2, 7))
        self.assertEqual(tf.end, datetime.datetime(2016, 2, 14))
        new_tf = Timeframe.get_timeframe("weekly", datetime.datetime(2016, 2, 13, 23, 59, 59, 99999))
        self.assertEqual(new_tf.to_dict(), tf.to_dict())

        tf = Timeframe.get_timeframe("monthly", datetime.datetime(2016, 2, 1))
        self.assertEqual(tf.start, datetime.datetime(2016, 2, 1))
        self.assertEqual(tf.end, datetime.datetime(2016, 3, 1))
        new_tf = Timeframe.get_timeframe("monthly", datetime.datetime(2016, 2, 29, 23, 59, 59, 99999))
        self.assertEqual(new_tf.to_dict(), tf.to_dict())

        tf = Timeframe.get_timeframe("quarterly", datetime.datetime(2016, 1, 1))
        self.assertEqual(tf.start, datetime.datetime(2016, 1, 1))
        self.assertEqual(tf.end, datetime.datetime(2016, 4, 1))
        new_tf = Timeframe.get_timeframe("quarterly", datetime.datetime(2016, 3, 31, 23, 59, 59, 99999))
        self.assertEqual(new_tf.to_dict(), tf.to_dict())

        tf = Timeframe.get_timeframe("yearly", datetime.datetime(2016, 1, 1))
        self.assertEqual(tf.start, datetime.datetime(2016, 1, 1))
        self.assertEqual(tf.end, datetime.datetime(2017, 1, 1))
        new_tf = Timeframe.get_timeframe("yearly", datetime.datetime(2016, 12, 31, 23, 59, 59, 99999))
        self.assertEqual(new_tf.to_dict(), tf.to_dict())

    def test_get_timeframes(self):
        with self.assertRaisesRegexp(AssertionError, "End must be after start"):
            Timeframe.get_timeframes("yearly", datetime.datetime(2016, 1, 2), datetime.datetime(2016, 1, 1))

        start = datetime.datetime(2016, 1, 1)
        end = datetime.datetime(2017, 1, 1) ## Should not include intervals starting on this date / time

        tfs = Timeframe.get_timeframes("daily", start, end)
        self.assertEqual(len(tfs), 366)
        for x in tfs:
            self.assertEqual(x.frequency_name, "daily")

        tfs = Timeframe.get_timeframes("weekly", start, end)
        self.assertEqual(len(tfs), 53)
        for x in tfs:
            self.assertEqual(x.start.weekday(), 6)
            self.assertEqual(x.frequency_name, "weekly")

        tfs = Timeframe.get_timeframes("monthly", start, end)
        self.assertEqual(len(tfs), 12)
        for x in tfs:
            self.assertEqual(x.start.day, 1)
            self.assertEqual(x.end.day, 1)
            self.assertEqual(x.frequency_name, "monthly")

        tfs = Timeframe.get_timeframes("quarterly", start, end)
        self.assertEqual(len(tfs), 4)
        for x in tfs:
            self.assertEqual(x.start.day, 1)
            self.assertEqual(x.end.day, 1)
            self.assertEqual(x.start.month % 3, 1)
            self.assertEqual(x.end.month % 3, 1)
            self.assertEqual(x.frequency_name, "quarterly")
            
        tfs = Timeframe.get_timeframes("yearly", start, end)
        self.assertEqual(len(tfs), 1)
        for x in tfs:
            self.assertEqual(x.start.day, 1)
            self.assertEqual(x.end.day, 1)
            self.assertEqual(x.start.month, 1)
            self.assertEqual(x.end.month, 1)
            self.assertEqual(x.frequency_name, "yearly")

        end = datetime.datetime(2017, 1, 1, 1) ## Should include intervals starting on this date

        tfs = Timeframe.get_timeframes("daily", start, end)
        self.assertEqual(len(tfs), 367)
        for x in tfs:
            self.assertEqual(x.frequency_name, "daily")

        tfs = Timeframe.get_timeframes("monthly", start, end)
        self.assertEqual(len(tfs), 13)
        for x in tfs:
            self.assertEqual(x.start.day, 1)
            self.assertEqual(x.end.day, 1)
            self.assertEqual(x.frequency_name, "monthly")

        tfs = Timeframe.get_timeframes("quarterly", start, end)
        self.assertEqual(len(tfs), 5)
        for x in tfs:
            self.assertEqual(x.start.day, 1)
            self.assertEqual(x.end.day, 1)
            self.assertEqual(x.start.month % 3, 1)
            self.assertEqual(x.end.month % 3, 1)
            self.assertEqual(x.frequency_name, "quarterly")

    def test_sub_timeframes(self):
        tf = Timeframe.get_timeframe("yearly", datetime.datetime(2016, 1, 1))
        tfs = tf.sub_timeframes("daily")
        start = tf.start
        self.assertEqual(len(tfs), 366)
        for x in tfs:
            self.assertEqual(start, x.start)
            start = start + datetime.timedelta(1)

    def test_persist(self):
        ## Test that data persists to the database
        tf = Timeframe("yearly", datetime.datetime(2016, 1, 1))
        tf.persist()
        self.assertTrue(tf.exists())

        check_tf = Timeframe.pull_by_start_end(tf.start, tf.end).to_dict()
        for key, val in tf.to_dict().iteritems():
            self.assertEqual(check_tf[key], val)

        ## Test that you can persist the same one twice without duplicate key, etc errors
        tf.persist()

    def test_pull_by_start_end(self):
        ## Pulling by start / end should return None if none exists:
        self.assertIsNone(Timeframe.pull_by_start_end(datetime.datetime(2016, 1, 1), datetime.datetime(2017, 1, 1)))
        tf = Timeframe("yearly", datetime.datetime(2016, 1, 1))
        tf.persist()
        self.assertTrue(tf.exists())

        check_tf = Timeframe.pull_by_start_end(tf.start, tf.end).to_dict()
        for key, val in tf.to_dict().iteritems():
            self.assertEqual(check_tf[key], val)

        ## Should *not* pull if the start is right and end is wrong or vice versa:
        self.assertIsNone(Timeframe.pull_by_start_end(tf.start, datetime.datetime(2016, 2, 1)))
        self.assertIsNone(Timeframe.pull_by_start_end(datetime.datetime(2016, 2, 1), tf.end))


    def test_pull_by_id(self):
        ## Test that a timeframe that exists can be pulled by ID
        self.assertIsNone(Timeframe.pull_by_id(0))
        
        tf = Timeframe("yearly", datetime.datetime(2016, 1, 1))
        tf.persist()
        self.assertTrue(tf.exists())

        check_tf = Timeframe.pull_by_id(tf.get_id()).to_dict()
        for key, val in tf.to_dict().iteritems():
            self.assertEqual(check_tf[key], val)

    def test_get_id(self):
        ## Test that a Timeframe that has just been persisted returns an ID
        tf = Timeframe("yearly", datetime.datetime(2016, 1, 1))
        tf.persist()
        self.assertIsNotNone(tf.get_id())
        
        ## Test that a timeframe pulled by id returns same id
        check_tf = Timeframe.pull_by_id(tf.get_id())
        self.assertEqual(check_tf.get_id(), tf.get_id())

        ## Test that a timeframe created by start / end persistes, then returns an ID
        tf = Timeframe("monthly", datetime.datetime(2016, 1, 1))
        self.assertIsNotNone(tf.get_id())
        self.assertTrue(tf.exists())
        self.assertNotEqual(tf.get_id(), check_tf.get_id())
        
        ## Test that a timeframe pulled by start / end returns an ID
        check_tf = Timeframe.pull_by_start_end(tf.start, tf.end)
        self.assertEqual(check_tf.get_id(), tf.get_id())

    def test_exists(self):
        tf = Timeframe("yearly", datetime.datetime(2016, 1, 1))
        self.assertFalse(tf.exists())
        tf.persist()
        self.assertTrue(tf.exists())

    

    




    



if __name__ == '__main__':
    unittest.main()
