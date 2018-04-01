import sys
import time
import sqlite3 as sql
from app import login_manager, db
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from Adafruit_IO import MQTTClient

ADAFRUIT_IO_KEY = '80009f64496041f79d5f440181eeb727'
ADAFRUIT_IO_USERNAME = 'caycay'


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


@login_manager.user_loader
def load_user(id):
     return getUserByID(id)

def create_user(username, email, password_hash):
	with sql.connect('database.db') as connection:
		cursor = connection.cursor()
		cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (?,?,?)",(username, email, password_hash))
		connection.commit()



# Define callback functions which will be called when certain events happen.
def connected(client):
    # Connected function will be called when the client is connected to Adafruit IO.
    # This is a good place to subscribe to feed changes.  The client parameter
    # passed to this function is the Adafruit IO MQTT client so you can make
    # calls against it easily.
    print('Connected to Adafruit IO!  Listening for DemoFeed changes...')
    # Subscribe to changes on a feed named DemoFeed.
    client.subscribe('ComingHome')

def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print('Disconnected from Adafruit IO!')
    sys.exit(1)

def message(client, feed_id, payload):
    # Message function will be called when a subscribed feed has a new value.
    # The feed_id parameter identifies the feed, and the payload parameter has
    # the new value.
    print('Feed {0} received new value: {1}'.format(feed_id, payload))
    # use new payload as signal to trigger another action ->displaying a message

def startMQTT():
	client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
	# Setup the callback functions defined above.
	client.on_connect    = connected
	client.on_disconnect = disconnected
	client.on_message    = message
	client.connect()
	client.loop_background()

