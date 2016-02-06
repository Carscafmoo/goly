"""This package defines the timeframe class for goly, including ORM nonsense"""
from goly import db, errors
from sqlalchemy import MetaData, Table
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
        if (self.frequency_name == 'monthly'): assert start.day == 1, "Monthly timeframes must begin on the first of the month"
        elif (self.frequency_name == 'quarterly'): assert start.day == start.month % 3 == 1, "Quarterly timeframes must begin on January, April, July, or October 1"
        elif (self.frequency_name == 'yearly'): assert start.day == start.month == 1, "Yearly timeframes must begin on Jan 1"

        return start

    def _calculate_end(self):
        freq = self.frequency_name
        if (freq == 'daily'): return self.start + datetime.timedelta(1)
        if (freq == 'weekly'): return self.start + datetime.timedelta(7)
        if (freq == 'monthly'): return self.start + dateutil.relativedelta.relativedelta(months=+1)
        if (freq == 'quarterly'): return self.start + dateutil.relativedelta.relativedelta(months=+3)
        if (freq == 'yearly'): return self.start + dateutil.relativedelta.relativedelta(years=+1)


