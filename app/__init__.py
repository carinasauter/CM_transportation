from flask import Flask
from flask_mqtt import Mqtt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from threading import Lock
import eventlet
eventlet.monkey_patch()
from flask_bootstrap import Bootstrap


app = Flask(__name__)

app.config.from_object('config')
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
async_mode = 'eventlet'
socketio = SocketIO(app, async_mode=async_mode, logger=True, engineio_logger=True)
thread = None
thread_lock = Lock()

bootstrap = Bootstrap(app)
# app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MQTT_BROKER_URL'] = 'io.adafruit.com'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = 'caycay'
app.config['MQTT_PASSWORD'] = '80009f64496041f79d5f440181eeb727'
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False

mqtt = Mqtt(app)


from app import views, models


