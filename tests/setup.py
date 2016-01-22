import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import datetime
from goly import db
from goly.models.user import User
import copy

test_user = User("test@example.com", "test-pass", "first", "last")

def create_test_users():
    for x in range(ord('a'), ord('a') + 26):
        x = chr(x)
        email = "test_" + str(x) + "@example.com"
        new_user = User(email, "test-pass", x + "_first", x + "_last")
        new_user.registered = new_user.registered_on - datetime.timedelta(hours=30-(ord(x)-ord('a')))
        db.session.add(new_user)

    db.session.commit()

def create_test_user():
    get_test_user().persist()

    return test_user

def get_test_user():
    return copy.deepcopy(test_user)