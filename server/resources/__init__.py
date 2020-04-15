from flask import Blueprint
from flask_restx import Api

from .deployment import api as deployment_ns

blueprint = Blueprint('api', __name__)

api = Api(blueprint,
    title='Flask, flask-socketio, test server',
    version='3.0',
    description='This is the API definition for testing Flask, flask-socketio rabbitMQ integration',
    doc='/documentation'
)

api.add_namespace(deployment_ns)
