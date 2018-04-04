from flask import Flask
from flask_mqtt import Mqtt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
import eventlet
eventlet.monkey_patch()


app = Flask(__name__)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
async_mode = 'eventlet'
socketio = SocketIO(app, async_mode=async_mode, logger=True, engineio_logger=True)

app.config['SECRET'] = 'my secret key'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MQTT_BROKER_URL'] = 'broker.hivemq.com'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = ''
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False


app.config.from_object('config')




mqtt = Mqtt(app)


from app import views, models


