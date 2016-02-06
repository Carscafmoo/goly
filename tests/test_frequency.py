import setup
import unittest
from goly import db
from goly.models.frequency import Frequency
class TestFrequency(unittest.TestCase):
    def test_cache(self):
        self.assertEqual(len(Frequency.id_cache), 5)
        self.assertEqual(len(Frequency.name_cache), 5)

    def test_get_by_name(self):
        ## Fails on bogus name:
        with self.assertRaisesRegexp(AssertionError, "Frequency must be one of"):
            Frequency.get_id_by_name("Bogus")
        
        id = Frequency.get_id_by_name('weekly')
        self.assertEqual(Frequency.get_name_by_id(id), 'weekly')

if __name__ == "__main__":
    unittest.main()