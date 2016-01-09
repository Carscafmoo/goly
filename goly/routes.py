from goly import app, db
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask import request, render_template, redirect, flash, url_for
from models.user import User

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/register' , methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    user = User(request.form['email'], request.form['password'], request.form['first_name'], request.form['last_name'])
    user.persist()
    flash('User successfully registered')
    return redirect(url_for('login'))
 
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    email = request.form['email']
    password = request.form['password']
    registered_user = User.query.filter_by(email=email,password=password).first()
    if not registered_user:
        flash('Username or Password is invalid' , 'error')
        
        return redirect(url_for('login'))
    
    login_user(registered_user)
    flash('Logged in successfully')
    
    return redirect(request.args.get('next') or url_for('index'))

@app.route('/')
@login_required
def index():
    return "Hello World!"

