import eventlet
eventlet.monkey_patch()

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

from .config import Config

db = SQLAlchemy()

socketio = SocketIO()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=False)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_object(Config)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    db.init_app(app)

    # socketio.init_app(app, cors_allowed_origins='*', logger=True)
    socketio.init_app(app, cors_allowed_origins='*', message_queue='amqp://', logger=True)

    CORS(app)

    # Register Blueprints
    from .resources import blueprint as api
    app.register_blueprint(api)

    return app