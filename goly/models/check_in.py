"""This package defines the goal instance class for goly, including ORM nonsense"""
from goly import db, errors
from sqlalchemy import MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates
import datetime
import json
from goly.models.user import User
from goly.models.goal import Goal
from goly.models.timeframe import Timeframe
import werkzeug.local
md = MetaData(bind=db.engine)
goal = Table('check_in', md, autoload=True)
Base = declarative_base(metadata=md)

class CheckIn(Base, db.Model):
    __table__ = goal_instance

    def __init__(goal, timeframe, value):
        self.goal = goal ## have to do something about this yeah?
        self.timeframe = timeframe ## have to do something about this, yeah?
        self.value = value

    @validates('goal')
    def validate_goal(self, key, goal):
        ## Needs to be a goal,
        ## set the id
        ## Keep the goal itself around as cache for to_dict()
        
        pass

    @validates('timeframe')
    def validate_timeframe(self, key, timeframe):
        ## Needs to be a timeframe
        ## Pull the ID if exists, otherwise create
        ## Keep the TF itself as cache for to_dict()
        ## Ensure that TF and Goal have matching frequencies -- is this true?? 
        # check-in frequency should match this frequency; example: want to work out 5x a week, asked nightly
        # Should have 7 check-ins in the week.
        # @TODO: Convert check-in freq to point to "frequency"
        # @TODO: This timeframe must conform to check-in frequency
        # @TODO: Implement "sub-timeframe" construct -- given a timeframe of type X, find all smaller timeframes of type Y
        #   e.g., given a weekly timeframe, find all constituent daily timeframes
        # @TODO: Don't let people choose mis-aligned timeframes (e.g., a check-in timeframe of weekly for monthly stuff)?
        pass

    @validates('value'):
    def validate_value(self, key, value):
        ## Confirm that value conforms to goal type (e.g., binary is boolean, numeric is a number)
