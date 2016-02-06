import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import datetime
from goly import db
from goly.models.user import User
from goly.models.goal import Goal
import copy
import json

test_user_pass = "test-pass"
test_user_name = "test@example.com"
test_user = User(test_user_name, test_user_pass, "first", "last")

other_user_name = "otheruser@exmaple.com"
other_user_pass = "test-pass"
other_user = User(other_user_name, other_user_pass, "other", "user")

def create_test_users():
    for x in range(ord('a'), ord('a') + 26):
        x = chr(x)
        email = "test_" + str(x) + "@example.com"
        new_user = User(email, "test-pass", x + "_first", x + "_last")
        new_user.registered = new_user.registered_on - datetime.timedelta(hours=30-(ord(x)-ord('a')))
        db.session.add(new_user)

    db.session.flush()
    db.session.commit()

def create_test_user():
    test_user = get_test_user()
    if (not test_user.exists()):
        test_user.persist()

    return test_user


def get_test_user():
    return copy.deepcopy(test_user)

def get_other_user():
    return copy.deepcopy(other_user)

def create_other_user():
    other_user = get_other_user()
    if (not other_user.exists()):
        other_user.persist()

    return other_user


def create_test_goals():
    user = create_test_user()
    for x in range(ord('a'), ord('a') + 25):
        x = chr(x)
        name = "test goal " + str(x)
        new_goal = Goal(user, name, "Is this a test?", "daily", 10, "numeric", "daily")
        new_goal.created = new_goal.created - datetime.timedelta(hours=30-(ord(x)-ord('a')))
        db.session.add(new_goal)
    db.session.flush()
    db.session.commit()

def assertInvalidCredentials(test, res):
    """Logic for asserting that credentials passed were invalid"""
    data = json.loads(res.data)
    test.assertIn('detail', data)
    test.assertIn('Invalid credentials', data['detail'])
    test.assertEqual(res.status_code, 401)

def assertOk(test, res, code=200):
    test.assertEqual(res.status_code, code)

def assertRequiresLogin(test, res):
    test.assertEqual(res.status_code, 401)
    data = json.loads(res.data)
    test.assertIn('detail', data)
    test.assertIn("You must login to view this page", data['detail'])

def assertInvalid(test, res, missing_field):
    test.assertEqual(res.status_code, 400)
    data = json.loads(res.data)
    test.assertIn('detail', data)
    test.assertIn(missing_field, data['detail'])

def assertBadData(test, res, message):
    test.assertEqual(res.status_code, 400)
    data = json.loads(res.data)
    test.assertIn('detail', data)
    test.assertIn(message, data['detail'])

def assert404(test, res):
    test.assertEqual(res.status_code, 404)
    data = json.loads(res.data)
    test.assertIn("detail", data)
    test.assertIn("does not exist", data['detail'])
