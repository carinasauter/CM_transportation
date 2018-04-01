from flask import render_template, redirect, request, url_for, flash
from app import app, models, db, login_manager
from .forms import LoginForm, SignUpForm
from .models import *
import requests
import json
from flask_login import current_user, login_user, logout_user
from app.models import User
from flask_login import login_required
from werkzeug.security import generate_password_hash, check_password_hash
from Adafruit_IO import *
import time
import sys

ADAFRUIT_IO_KEY = '80009f64496041f79d5f440181eeb727'
ADAFRUIT_IO_USERNAME = 'caycay'


@app.route('/triggerComeHome')
def triggerComeHome():
    aio = Client(ADAFRUIT_IO_KEY)
    aio.send('comeHome', 0)
    print("Come Home!")
    startMQTT();
    data = {}
    return json.dumps(data)

@app.route('/getLocation')
def getLocation():
    aio = Client(ADAFRUIT_IO_KEY)
    aio.send('locationRequest', 1)
    print("Location request sent!")
    data = requests.get('https://io.adafruit.com/api/v2/' + ADAFRUIT_IO_USERNAME + '/feeds/gps/data/last?X-AIO-Key=' + ADAFRUIT_IO_KEY).content.decode("utf-8")
    data = json.loads(data)
    location_data = data['location']
    longitude = location_data['lon']
    latitude = location_data['lat']
    timestamp = data['created_at']
    return json.dumps(data)


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('display_info'))
    else:
        # we should have a landing page for user who have not logged in or signed up
        return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        user = getUserByUsername(username) #checks if user already exists
        if user is not None:
            # in this case user with this username exists already
            return render_template('signup.html', title = "Sign Up", form = form)
        # in case it does not exist
        password_hash = generate_password_hash(password)
        create_user(username, email, password_hash) # creates user in database
        userID = getUserID(username)
        user = User(userID, username, email, password_hash)
        login_user(user)
        return redirect(url_for('index'))
    return render_template('signup.html', title = "Sign Up", form = form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        comparedUser = getUserByUsername(username)
        if comparedUser is None or not check_password_hash(comparedUser.password_hash, password):
            return redirect(url_for('login'))
        login_user(comparedUser, remember = form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Log In', form=form)


@app.route('/protected')
@login_required
def protected():
    return 'Logged in as: ' + current_user.username


@app.route('/info', methods=['GET', 'POST'])
@login_required
def display_info():
    return render_template('info.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'))

