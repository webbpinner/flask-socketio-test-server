from flask_restx import Resource, reqparse, Namespace, fields
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError
from datetime import datetime
import json

from ..models.deployment import DeploymentModel
from .. import socketio

api = Namespace('deployments', description='Deployments', path='/api/v1')

deploymentModel = api.model('Deployment', {
    'id': fields.Integer(required=True, description='The deployment identifier'),
    'name': fields.String(required=True, description='The deployment\'s name')
})

deploymentListModel = api.model('DeploymentList', {
    'deployments': fields.List(fields.Nested(deploymentModel, skip_none=True))
})

_deployment_put_payload = reqparse.RequestParser()
_deployment_put_payload.add_argument('name',
                            type=str,
                            help="A shortname for the deployment."
                            )

@api.route('/deployment/<deployment_id>')
@api.param('deployment_id', 'The deployment identifier')
class Deployment(Resource):

    @socketio.on('connect', namespace="/deployments")
    def connect():
        print('client connected to deployments namespace')

    @socketio.on('disconnect', namespace="/deployments")
    def disconnect():
        print('client disconnected from deployments namespace')

    @socketio.on('deployment_updated')
    def handle_new_deployment(deployment):
        print('received new deployment ' + json.dumps(deployment.json()))
        socketio.emit('deployment_updated', deployment.json(), broadcast=True, namespace='/deployments')

    @classmethod
    @api.doc('update_deployment')
    @api.expect(_deployment_put_payload)
    @api.response(204, 'Resource Updated')
    def put(cls, deployment_id: int):
        """
        Update an deployment definition based on the definition's id.
        """

        data = _deployment_put_payload.parse_args()

        deployment = DeploymentModel.find_by_id(deployment_id)

        if deployment:
            if data['name']:
                deployment.name = data['name']

        else:
            raise NotFound('Deployment does not exist.')

        try:
            deployment.save_to_db()
            cls.handle_new_deployment(deployment)
        except Exception as error:
            print(error)
            raise InternalServerError("An error occurred saving to database.")

        return None, 204


@api.route('/deployments')
class DeploymentList(Resource):
    @api.doc('get_deployment_list')
    @api.marshal_with(deploymentListModel, 'Success', code=200, skip_none=True)
    def get(self):
        """
        Retrieve the list of deployment definitions.
        """

        deployments = DeploymentModel.find_all()
        if len(deployments) == 0:
            raise NotFound("No deployments found")

        return {'deployments': [deployment.json() for deployment in deployments]}, 200
