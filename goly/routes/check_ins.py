from flask_api.status import HTTP_200_OK
from goly import app, db
from flask_login import login_user, logout_user, current_user, login_required
from flask import request, jsonify
from goly.models.goal import Goal
from goly.models.user import User
from goly.models.check_in import CheckIn
from goly.models.timeframe import Timeframe
from goly.errors import NotFoundError, UnauthorizedError, InvalidRequest
from goly.routes import validate_form, empty_ok, validate_sort
import datetime

@app.route("/goals/<id>/check-ins/", methods=['POST'])
@login_required
def check_in(id):
    validate_form(request.form, ["value"])
    goal = Goal.pull_by_id(id)
    if (not goal):
        raise NotFoundError()
    
    if goal.user != current_user.get_id():
        raise UnauthorizedError
    
    if ('timeframe' in request.form):
        timeframe = Timeframe.pull_by_id(request.form['timeframe'])
    else:
        timeframe = Timeframe.get_current_timeframe(goal.check_in_frequency_name)

    check_in = CheckIn(goal, timeframe, request.form['value'])
    return_code = 200 if check_in.exists() else 201
    check_in.persist()

    return check_in.to_json(), return_code

@app.route("/goals/<id>/check-ins/current/", methods=['GET'])
@login_required
def get_current_check_in(id):
    """Get the current check-in for a given goal.  Returns 404 if the current check-in or goal does not exist"""
    goal = Goal.pull_by_id(id)
    if (not goal):
        raise NotFoundError()
    
    if goal.user != current_user.get_id():
        raise UnauthorizedError
    
    check_in = CheckIn.pull_by_goal_timeframe(id, Timeframe.get_current_timeframe(goal.check_in_frequency_name).get_id())
    if (not check_in):
        raise NotFoundError()

    return check_in.to_json(), 200


@app.route("/goals/<id>/check-ins/<tfid>/", methods=['GET'])
@login_required
def get_check_in(id, tfid):
    """Get the check-in for a given timeframe.  Returns 404 if there is no check-in for that timeframe"""
    goal = Goal.pull_by_id(id)
    if (not goal):
        raise NotFoundError()
    
    if goal.user != current_user.get_id():
        raise UnauthorizedError
    
    check_in = CheckIn.pull_by_goal_timeframe(id, tfid)
    if (not check_in):
        raise NotFoundError()

    return check_in.to_json(), 200    

@app.route("/goals/<id>/check-ins/", methods=["GET"])
@login_required
def get_by_time(id):
    goal = Goal.pull_by_id(id)
    if (not goal):
        raise NotFoundError()
    
    if goal.user != current_user.get_id():
        raise UnauthorizedError

    if (not 'start' in request.args or not 'end' in request.args):
        raise InvalidRequest(["start and end are required parameters"])

    try:
        start = datetime.datetime.strptime(request.args['start'], "%Y-%m-%d %H:%M:%S")
        end = datetime.datetime.strptime(request.args['end'], "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        raise InvalidRequest([e.message])

    check_ins = CheckIn.pull_by_goal_start_end(id, start, end)

    return jsonify({"check-ins": [check_in.to_dict() for check_in in check_ins]}), 200

