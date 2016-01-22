from goly import app, db
from goly.models.goal import Goal
from flask_api.exceptions import AuthenticationFailed
from flask_api.status import HTTP_200_OK
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask import request, g, jsonify
from goly.errors import UnauthorizedError, ResourceAlreadyExistsError, InvalidRequest, NotFoundError

@app.route("/goals/test")
def test():
    return "{}", HTTP_200_OK
