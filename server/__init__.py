import eventlet
eventlet.monkey_patch()

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

from .config import Config

db = SQLAlchemy()

# socketio = SocketIO(cors_allowed_origins='*', message_queue='amqp://', channel='rt_updates', async_mode='eventlet', logger=True)
socketio = SocketIO(cors_allowed_origins='*', logger=True)

from .resources import blueprint as api

def create_app(test_config=None, debug=False, *args, **kwargs):
    """Create an application."""
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_object(Config)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    db.init_app(app)
    socketio.init_app(app)
    CORS(app)

    with app.app_context():

        # Register Blueprints
        app.register_blueprint(api)

        return app