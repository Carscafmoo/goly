"""This package defines the timeframe class for goly, including ORM nonsense"""
from goly import db, errors
from sqlalchemy import MetaData, Table, orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates
import datetime
import dateutil.relativedelta
from goly.models.frequency import Frequency
md = MetaData(bind=db.engine)
timeframe = Table('timeframe', md, autoload=True)
Base = declarative_base(metadata=md)

class Timeframe(Base, db.Model):
    __table__ = timeframe

    def __init__(self, frequency, start):
        self.frequency = frequency
        self.start = start
        ## We go up to, but no including, the end. i.e., a time falls within a timeframe if time is in [start, end)
        self.end = self._calculate_end() 

    @orm.reconstructor
    def reconstruct(self):
        self.frequency_name = Frequency.get_name_by_id(self.frequency)

    @validates("frequency")
    def validate_frequency(self, key, freq):
        freq = freq.strip()
        self.frequency_name = freq
        freq = Frequency.get_id_by_name(freq) ## Assertion exists here

        return freq

    @validates("start")
    def validate_start(self, key, start):
        # Start must begin at midnight
        assert start.hour == start.minute == start.second == start.microsecond == 0, "Timeframe must begin at midnight!"
        if (self.frequency_name == 'weekly'): assert start.weekday() == 6, "Weekly timeframes must begin on Sunday"
        elif (self.frequency_name == 'monthly'): assert start.day == 1, "Monthly timeframes must begin on the first of the month"
        elif (self.frequency_name == 'quarterly'): assert start.day == start.month % 3 == 1, "Quarterly timeframes must begin on January, April, July, or October 1"
        elif (self.frequency_name == 'yearly'): assert start.day == start.month == 1, "Yearly timeframes must begin on Jan 1"

        return start

    def get_id(self):
        if (self.id): return self.id
        tf = self.pull_by_start_end(self.start, self.end)
        if (tf): 
            self.id = tf.get_id()
            return self.id

        self.persist()

        return self.get_id()
    
    def exists(self):
        if self.pull_by_start_end(self.start, self.end):
            return True

        return False

    def persist(self):
        """We don't error if we already exist; we just keep on truckin"""
        if (not self.exists()):
            db.session.add(self)
            db.session.commit()

    @classmethod
    def pull_by_id(self, id):
        return db.session.query(self).filter_by(id=id).first()

    @classmethod
    def pull_by_start_end(self, start, end):
        return db.session.query(self).filter_by(start=start).filter_by(end=end).first()

    def sub_timeframes(self, sub_frequency):
        return self.get_timeframes(sub_frequency, self.start, self.end)

    def _calculate_end(self):
        freq = self.frequency_name
        if (freq == 'daily'): return self.start + datetime.timedelta(1)
        if (freq == 'weekly'): return self.start + datetime.timedelta(7)
        if (freq == 'monthly'): return self.start + dateutil.relativedelta.relativedelta(months=+1)
        if (freq == 'quarterly'): return self.start + dateutil.relativedelta.relativedelta(months=+3)
        if (freq == 'yearly'): return self.start + dateutil.relativedelta.relativedelta(years=+1)

    def to_dict(self):
        return {
            "start": str(self.start),
            "end": str(self.end),
            "frequency": self.frequency_name
        }

    @classmethod 
    def get_most_recent_week_start(self, time):
        time = time + dateutil.relativedelta.relativedelta(days=-((time.weekday() + 1) % 7))
        
        return datetime.datetime(time.year, time.month, time.day)
            

    @classmethod
    def get_timeframe(self, frequency, time):
        """Return the timeframe at a given time, given the timeframe frequency

        Note that timeframes include their start time but not their end time, so if time is e.g.
        Jan 1, 2016 00:00:00, the correct yearly time frame is the one that begins Jan 1, 2016 00:00:00
        """
        if (frequency == 'daily'):
            return Timeframe(frequency, datetime.datetime(time.year, time.month, time.day))
        if (frequency == 'weekly'):
            return Timeframe(frequency, self.get_most_recent_week_start(time))
        if (frequency == 'monthly'): 
            return Timeframe(frequency, datetime.datetime(time.year, time.month, 1))
        if (frequency == 'quarterly'): 
            return Timeframe(frequency, datetime.datetime(time.year, time.month - (time.month - 1) % 3, 1))
        if (frequency == 'yearly'): 
            return Timeframe(frequency, datetime.datetime(time.year, 1, 1))

    @classmethod
    def get_current_timeframe(self, frequency):
        return self.get_timeframe(frequency, datetime.datetime.now())

    @classmethod
    def get_timeframes(self, frequency, start, end):
        """Return an array of all timeframes between start and end

        Includes start and end.  
        Note that a timeframe starting on the end time does not technically include the end time, so it is not included.
        Spillover is included (e.g., a monthly timeframe starting on a Tuesday and ending on a Wednesday
        would return the full beginning week and full end week if chopped weekly)
        """
        assert end >= start, "End must be after start."
        
        tfs = []
        tf = self.get_timeframe(frequency, start)
        while tf.start < end:
            tfs.append(tf)
            tf = Timeframe(frequency, tf._calculate_end())

        return tfs



