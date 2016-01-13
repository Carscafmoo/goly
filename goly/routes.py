from flask_api.exceptions import AuthenticationFailed
from flask_api.status import HTTP_200_OK
from goly import app, db
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask import request, g, jsonify
from goly.models.user import User
from goly.errors import UnauthorizedError, ResourceAlreadyExistsError

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user

@app.route('/register', methods=['POST'])
def register():
    user = User(request.form['email'], request.form['password'], request.form['first_name'], request.form['last_name'])
    user.persist()
    return_val = user.to_json()
    
    return return_val
 
@app.route('/login', methods=['POST'])
def login():
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
    
    return empty_ok()

@app.route('/logout')
def logout():
    logout_user()
    return empty_ok()

@app.route("/user/delete", methods=['POST']) # POST because you have to post your password
def delete_user():
    user = User.pull_by_email(request.form['email'])
    if (not user):
        raise UnauthorizedError()
    
    user.delete(request.form['password'])

    return empty_ok()

@app.route("/user/update-password", methods=['POST'])
def update_password():
    user = User.pull_by_email(request.form['email'])
    if (not user):
        raise UnauthorizedError
    user.update_password(request.form['old_password'], request.form['new_password'])

    return empty_ok()

@app.route('/')
@login_required
def index():
    return '{"data": "Hello, world"}', HTTP_200_OK


@app.errorhandler(ResourceAlreadyExistsError)
def handle_resource_already_exists(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

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

def empty_ok():
    return "{}", HTTP_200_OK
