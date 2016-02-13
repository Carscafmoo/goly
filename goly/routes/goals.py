from flask_api.status import HTTP_200_OK
from goly import app, db
from flask_login import login_user, logout_user, current_user, login_required
from flask import request, jsonify
from goly.models.goal import Goal
from goly.models.user import User
from goly.errors import NotFoundError, UnauthorizedError
from goly.routes import validate_form, empty_ok, validate_sort


@app.route("/goals/create/", methods=['POST'])
@login_required
def create_goal():
    validate_form(request.form, ["name", "prompt", "frequency", "target", "input_type", "check_in_frequency"])
    goal = Goal(current_user, 
        request.form['name'], 
        request.form['prompt'], 
        request.form['frequency'], 
        request.form['target'], 
        request.form['input_type'],
        request.form['check_in_frequency'])

    goal.persist()

    return goal.to_json(), 201

@app.route("/goals/delete/", methods=['POST'])
@login_required
def delete_goal():
    validate_form(request.form, ['id'])
    Goal.delete(current_user.get_id(), request.form['id'])

    return empty_ok(204)

@app.route("/goals/update/", methods=['POST'])
@login_required
def update_goal():
    validate_form(request.form, ['id'])
    goal = Goal.pull_by_id(request.form['id'])
    if (not goal): 
        raise NotFoundError()
    if (goal.user != current_user.get_id()):
        raise UnauthorizedError()
    goal.update(request.form)

    return empty_ok()

@app.route("/goals/users/me/", methods=['GET'])
@login_required
def get_my_goals():
    """Return all goals (public and private) for the current user"""
    validate_sort(request.args, ["id", "created", "name", "frequency"])
    goals = Goal.pull_by_user(current_user.get_id(), request.args, False)

    return jsonify({"goals": [x.to_dict() for x in goals]}), HTTP_200_OK

@app.route("/goals/users/<id>/", methods=["GET"])
@login_required
def get_goals_by_user(id):
    """Show all public goals for a given user"""
    user = User.pull_by_id(id)
    if (not user): 
        raise NotFoundError()

    validate_sort(request.args, ["id", "created", "name", "frequency"])
    goals = Goal.pull_by_user(id, request.args, True)

    return jsonify({"goals": [x.to_dict() for x in goals]}), HTTP_200_OK

@app.route("/goals/<id>/", methods=["GET"])
@login_required
def get_goal(id):
    goal = Goal.pull_by_id(id)
    if (not goal):
        raise NotFoundError()

    if (not goal.public and goal.user != current_user.get_id()):
        raise UnauthorizedError()

    return goal.to_json(), HTTP_200_OK


