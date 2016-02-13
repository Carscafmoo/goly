"""This package defines the goal instance class for goly, including ORM nonsense"""
from goly import db, errors
from sqlalchemy import MetaData, Table, orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates
import datetime
import json
from goly.models.user import User
from goly.models.goal import Goal
from goly.models.timeframe import Timeframe
import werkzeug.local
md = MetaData(bind=db.engine)
check_in = Table('check_in', md, autoload=True)
Base = declarative_base(metadata=md)

class CheckIn(Base, db.Model):
    __table__ = check_in

    def __init__(self, goal, timeframe, value):
        self.goal = goal 
        self.timeframe = timeframe 
        self.value = value
        self.timestamp = datetime.datetime.now()

    @validates('goal')
    def validate_goal(self, key, goal):
        assert isinstance(goal, Goal), "Passed goal must be a goal object!"
        self.goal_obj = goal

        return goal.get_id()

    @validates('timeframe')
    def validate_timeframe(self, key, timeframe):
        assert isinstance(timeframe, Timeframe), "Passed timeframe must be a timeframe object"
        assert timeframe.frequency == self.goal_obj.check_in_frequency, "Passed timeframe frequency must match goal's check-in frequency"
        self.timeframe_obj = timeframe

        return timeframe.get_id()

    @orm.reconstructor
    def reconstruct(self):
        self.goal_obj = Goal.pull_by_id(self.goal)
        self.timeframe_obj = Timeframe.pull_by_id(self.timeframe)


    @validates('value')
    def validate_value(self, key, value):
        if (self.goal_obj.input_type == 'numeric'): # Technically "True" comes through as 1
            assert isinstance(value, (int, long)) or (isinstance(value, (str, unicode)) and value.isdigit()), "Value must be numeric if input_type is numeric!"
            value = int(value)
        else: 
            assert isinstance(value, bool) or value == 'True' or value == 'False', "Value must be a boolean if input_type is binary!"
            value = 1 if value == 'True' or value == True else 0

        return value

    def get_id(self):
        if (not self.id):
            self.id = self._pull_self().get_id()

        return self.id

    def persist(self):
        """Persist the check-in.  Overwrite if already in the DB"""
        existing = self._pull_self()
        if existing:
            existing.value = self.value
        else: 
            existing = self
            db.session.add(existing)

        existing.timestamp = datetime.datetime.now()
        db.session.flush()
        db.session.commit()

    def exists(self):
        if (self._pull_self()):
            return True

        return False

    def to_dict(self):
        """Dict returns the goal ID but the timeframe as an object

        This should make it much easier to display?"""
        return {
            "id": self.get_id(),
            "goal": self.goal,
            "timeframe": self.timeframe_obj.to_dict(),
            "value": self.value
        }        

    def to_json(self):
        return json.dumps(self.to_dict())

    def _pull_self(self):
        return self.pull_by_goal_timeframe(self.goal, self.timeframe)

    def destroy(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def pull_by_goal_timeframe(self, goal, timeframe):
        """Pull a check-in out of the database by its goal and timeframe.
        goal -- goal id
        timeframe -- timeframe ID"""
        return db.session.query(self).filter_by(goal=goal).filter_by(timeframe=timeframe).first()

    @classmethod
    def pull_by_id(self, id):
        return db.session.query(self).filter_by(id=id).first()

    @classmethod
    def pull_by_goal_timeframes(self, goal, timeframes):
        """Return an array of check-ins given a goal ID and a list of timeframe IDs"""
        return db.session.query(self).filter_by(goal=goal).filter(CheckIn.timeframe.in_(timeframes)).all()

    @classmethod
    def pull_by_goal_start_end(self, goal, start, end):
        """Return an array of check-ins given a goal ID and start date and an end date"""
        goal = Goal.pull_by_id(goal)
        timeframes = Timeframe.get_timeframes(goal.check_in_frequency_name, start, end)
        timeframes = [x.get_id() for x in timeframes]

        return self.pull_by_goal_timeframes(goal.get_id(), timeframes)




