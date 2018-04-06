import sys
import time
import eventlet
eventlet.monkey_patch()
import sqlite3 as sql
from flask_mqtt import Mqtt
from flask import render_template, redirect, request, url_for, Flask
from app import login_manager, db, socketio, mqtt
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from Adafruit_IO import MQTTClient
from flask_socketio import SocketIO, emit


class User(UserMixin):

	def __init__(self, id_number, username, email, password_hash):
		self.id = id_number;
		self.username = username
		self.email = email
		self.password_hash = password_hash


""" Takes a username as parameter and checks in the database. If the user exists, 
returns user object. If not, returns None.
"""
def getUserByUsername(query):
	with sql.connect('database.db') as connection:
		connection.row_factory = sql.Row
		cursor = connection.cursor()
		cursor.execute("SELECT * FROM users WHERE username=?", (query,))
		result = cursor.fetchall()
		if len(result) == 0:
			return None
		else:
			row = result[0]
			user = User(row[0], query, row[2], row[3])
			return user


""" Takes a userID as parameter and checks in the database. If the user exists, 
returns user object. If not, returns None.
"""
def getUserByID(query):
	with sql.connect('database.db') as connection:
		connection.row_factory = sql.Row
		cursor = connection.cursor()
		cursor.execute("SELECT * FROM users WHERE user_id=?", (query,))
		result = cursor.fetchall()
		if len(result) == 0:
			return None
		else:
			row = result[0]
			user = User(query, row[1], row[2], row[3])
			return user


""" Takes a username as parameter and 
checks with user ID is associated with that username.
Returns the userID. Assumes the username exists.
"""
def getUserID(query):
	with sql.connect('database.db') as connection:
		connection.row_factory = sql.Row
		cursor = connection.cursor()
		cursor.execute("SELECT * FROM users WHERE username=?", (query,))
		result = cursor.fetchall()
		return result[0][0]


# Helper function for login process
@login_manager.user_loader
def load_user(id):
     return getUserByID(id)

""" Creates a new user in database based on form input
"""
def create_user(username, email, password_hash):
	with sql.connect('database.db') as connection:
		cursor = connection.cursor()
		cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (?,?,?)",(username, email, password_hash))
		connection.commit()

""" When new value is added to subscribed to feed 
(coming Home in this case), signal is sent to frontend javascript
"""
@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    socketio.emit('my_response',  "hello")