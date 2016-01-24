from flask_api.exceptions import AuthenticationFailed
from flask_api.status import HTTP_200_OK
from goly import app, db
from flask_login import login_user, logout_user, current_user, login_required
from flask import request, g, jsonify
from goly.models.goal import Goal
from goly.models.user import User
from goly.errors import InvalidRequest, NotFoundError
from goly.routes import validate_form, empty_ok, login_manager


@app.route("/goals/create/", methods=['POST'])
@login_required
def create_goal():
    validate_form(request.form, ["name", "prompt", "frequency", "target", "input_type"])
    goal = Goal(current_user, request.form['name'], request.form['prompt'], request.form['frequency'], request.form['target'], request.form['input_type'])

    goal.persist()

    return goal.to_json(), 201

@app.route("/goals/delete/", methods=['POST'])
@login_required
def delete_goal():
    validate_form(request.form, ['id'])
    Goal.delete(current_user.get_id(), request.form['id'])

    return empty_ok(204)

