from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_user, logout_user, current_user
from passlib.hash import sha256_crypt
from . import models

bp = Blueprint('auth', __name__)
db = models.db

@bp.route('/login', methods=['GET'])
def login():
    return render_template('auth/login.html')

@bp.route('/login', methods=['POST'])
def login_post():
    user = models.User.query.filter_by(email=request.form.get('email')).first()
    if not user or not sha256_crypt.verify(request.form.get('password'), user.password):
        return render_template('auth/login.html', error_msg='Authentication failure.')

    login_user(user)
    return redirect(url_for('map.show'))

@bp.route('/signup', methods=['GET'])
def signup():
    return render_template('auth/signup.html', form={})

@bp.route('/signup', methods=['POST'])
def signup_post():
    email     = request.form.get('email')
    name      = request.form.get('name')
    company   = request.form.get('company')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')

    # Check if the user already exists
    user = models.User.query.filter_by(email=email).first()
    if user:
        return render_template('auth/signup.html', form=request.form, error_msg='This user already exists.')

    try:
        user = models.User(email, password1, password2, name, company)
        models.db.session.add(user)
        models.db.session.commit()
    except models.PasswordsDontMatchException:
        return render_template('auth/signup.html', form=request.form, error_msg='The passwords do not match. Try again.')

    return render_template('auth/login.html', info_msg='User registered. You can log in now.')

@bp.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return login()

@bp.route('/profile', methods=['GET'])
def profile():
    return render_template('auth/profile.html', user=current_user)

@bp.route('/profile', methods=['POST'])
def profile_post():
    current_user.name = request.form.get('name')
    current_user.company = request.form.get('company')

    password1 = request.form.get('new_password1')
    password2 = request.form.get('new_password2')
    if password1:
        if password1 == password2:
            current_user.password = sha256_crypt.encrypt(password1)
        else:
            return render_template('auth/profile.html', user=current_user, error_msg='New passwords do not match.')

    models.db.session.commit()
    return render_template('auth/profile.html', user=current_user, info_msg='Profile updated.')
