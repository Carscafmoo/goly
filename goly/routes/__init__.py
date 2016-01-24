from flask_api.exceptions import AuthenticationFailed
from flask_api.status import HTTP_200_OK
from goly import app
from flask_login import LoginManager
from flask import jsonify
from goly.errors import UnauthorizedError, ResourceAlreadyExistsError, InvalidRequest, NotFoundError

login_manager = LoginManager()
login_manager.init_app(app)


@app.errorhandler(ResourceAlreadyExistsError)
def handle_resource_already_exists(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    
    return response

def require_login_error():
    response = jsonify({"detail": "You must login to view this page."})
    response.status_code = 401
    
    return response

login_manager.unauthorized_handler(require_login_error)

@app.errorhandler(UnauthorizedError)
def custom_401(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    
    return response

@app.errorhandler(AuthenticationFailed)
def handle_auth_failure(error):
    response = jsonify({"detail": str(error)})
    response.status_code = 401
    
    return response

@app.errorhandler(InvalidRequest)
def handle_invalid_request(error):
    response = jsonify({"detail": str(error)})
    response.status_code = 400

    return response

@app.errorhandler(NotFoundError)
def handle_not_found(error):
    response = jsonify({"detail": str(error)})
    response.status_code = 404

    return response

@app.errorhandler(AssertionError)
def handle_assertion_error(error):
    response = jsonify({"detail": str(error)})
    response.status_code = 400

    return response


def empty_ok(status=HTTP_200_OK):
    return "{}", status

def validate_form(form, fields):
    missing_fields = set(fields) - set(form.keys())
    if (missing_fields):
        raise InvalidRequest(missing_fields)