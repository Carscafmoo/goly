import flask_api
from goly import app, db
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask import request, g
from models.user import User

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user
    print g.user

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
        raise flask_api.exceptions.AuthenticationFailed(email + " is not a registered user email")

    if not registered_user.check_password(password):
        raise flask_api.exceptions.AuthenticationFailed("Incorrect password")

    login_user(registered_user, remember=remember_user)
    
    return "", flask_api.status.HTTP_200_OK

@app.route('/logout')
def logout():
    logout_user()
    return "", flask_api.status.HTTP_200_OK

@app.route('/')
@login_required
def index():
    return '{"data": "Hello, world"}', flask_api.status.HTTP_200_OK

