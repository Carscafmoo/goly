import setup
import unittest
from goly.models.timeframe import Timeframe
from goly import db
import datetime

class TestTimeframe(unittest.TestCase):
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
        now = datetime.datetime(2016, 1, 1)
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






if __name__ == '__main__':
    unittest.main()
