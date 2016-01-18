from flask_api.exceptions import AuthenticationFailed
from flask_api.status import HTTP_200_OK
from goly import app, db
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask import request, g, jsonify
from goly.models.user import User
from goly.errors import UnauthorizedError, ResourceAlreadyExistsError, InvalidRequest, NotFoundError

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user

@app.route('/register/', methods=['POST'])
def register():
    validate_form(request.form, ['email', 'password', 'first_name', 'last_name'])
    user = User(request.form['email'], request.form['password'], request.form['first_name'], request.form['last_name'])
    user.persist()
    return_val = user.to_json()
    
    return return_val, 201
 
@app.route('/login/', methods=['POST'])
def login():
    validate_form(request.form, ['email', 'password'])
    email = request.form['email']
    password = request.form['password']
    remember_user = False
    if (request.form.has_key('remember')):
        remember_user = request.form['remember']
    registered_user = User.query.filter_by(email=email).first()
    if not registered_user:
        raise AuthenticationFailed(email + " is not a registered user email")

    if not registered_user.check_password(password):
        raise AuthenticationFailed("Incorrect password")

    login_user(registered_user, remember=remember_user)
    
    return empty_ok(201)

@app.route('/logout/', methods=['POST'])
def logout():
    logout_user()
    return empty_ok(204)

@app.route("/users/delete/", methods=['POST']) # POST because you have to post your password
def delete_user():
    validate_form(request.form, ['email', 'password'])
    user = User.pull_by_email(request.form['email'])
    if (not user):
        raise UnauthorizedError()
    
    user.delete(request.form['password'])

    return empty_ok(204)

@app.route("/users/update-password/", methods=['POST'])
def update_password():
    validate_form(request.form, ['email', 'old_password', 'new_password'])
    user = User.pull_by_email(request.form['email'])
    if (not user):
        raise UnauthorizedError
    user.update_password(request.form['old_password'], request.form['new_password'])

    return empty_ok()

@app.route("/users/update-email/", methods=['POST'])
def update_email():
    validate_form(request.form, ['old_email', 'new_email', 'password'])
    user = User.pull_by_email(request.form['old_email'])
    if (not user):
        raise UnauthorizedError
    user.update_email(request.form['new_email'], request.form['password'])

    return empty_ok()

@app.route("/users/update/", methods=['POST'])
def update():
    validate_form(request.form, ['email', 'password'])
    user = User.pull_by_email(request.form['email'])
    if (not user):
        raise UnauthorizedError
    if (not user.check_password(request.form['password'])):
        raise UnauthorizedError

    user.update(request.form)

    return empty_ok()

@app.route("/users/me/")
@login_required
def get_me():
    return current_user.to_json(), HTTP_200_OK

@app.route("/users/<id>/")
@login_required
def get_user(id):
    user = User.pull_by_id(id)
    if (not user):
        raise NotFoundError()

    return user.to_json(), HTTP_200_OK

@app.route('/users/index/', methods=['GET'])
@login_required
def index():
    if ('sort_order' in request.args):
        if (request.args['sort_order'] not in ['asc', 'desc']):
            raise InvalidRequest(['sort_order must be either asc or desc'])
    if ('sort' in request.args):
        if (request.args['sort'] not in ['first_name', 'last_name', 'id', 'email', 'registered_on']):
            raise InvalidRequest(['sort can only be one of first_name, last_name, id, email, registered_on'])
    
    ## We return an object rather than a list because of this obscure security issue: http://flask.pocoo.org/docs/0.10/security/#json-security
    return jsonify({"users": [x.to_dict() for x in User.pull(request.args)]}), HTTP_200_OK


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

def empty_ok(status=HTTP_200_OK):
    return "{}", status

def validate_form(form, fields):
    missing_fields = set(fields) - set(form.keys())
    if (missing_fields):
        raise InvalidRequest(missing_fields)

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