from flask_restx import Resource, reqparse, Namespace, fields
from flask_socketio import emit

from werkzeug.exceptions import BadRequest, NotFound, InternalServerError
from datetime import datetime

from ..models.deployment import DeploymentModel
import json

from .. import socketio

api = Namespace('deployments', description='Deployments', path='/api/v1')

deploymentModel = api.model('Deployment', {
    'id': fields.Integer(required=True, description='The deployment identifier'),
    'name': fields.String(required=True, description='The deployment\'s name'),
    'start_ts': fields.DateTime(required=True, description='The start time of the deployment'),
    'stop_ts': fields.DateTime(required=True, description='The stop time of the deployment'),
    'platform_id': fields.Integer(required=True, description='The deployment\'s parent_id'),
    'disabled': fields.Boolean(required=True, description='The deployment\'s disabled flag'),
})

deploymentListModel = api.model('DeploymentList', {
    'deployments': fields.List(fields.Nested(deploymentModel, skip_none=True))
})

_deployment_post_payload = reqparse.RequestParser()
_deployment_post_payload.add_argument('name',
                            type=str,
                            required=True,
                            help="A shortname for the deployment."
                            )
_deployment_post_payload.add_argument('start_ts',
                            type=lambda d: datetime.strptime(d, '%Y-%m-%dT%H:%M:%S.%fZ'),
                            required=True,
                            help="The start date/time for the deployment."
                            )
_deployment_post_payload.add_argument('stop_ts',
                            type=lambda d: datetime.strptime(d, '%Y-%m-%dT%H:%M:%S.%fZ'),
                            required=True,
                            help="The stop date/time for the deployment."
                            )
_deployment_post_payload.add_argument('platform_id',
                            type=int,
                            required=True,
                            help="The id of the platform for the deployment.",
                            )
_deployment_post_payload.add_argument('disabled',
                            type=bool,
                            default=False,
                            help="Is the deployment currently disabled."
                            )

_deployment_put_payload = reqparse.RequestParser()
_deployment_put_payload.add_argument('name',
                            type=str,
                            help="A shortname for the deployment."
                            )
_deployment_put_payload.add_argument('platform_id',
                            type=int,
                            help="The id of the platform for the deployment."
                            )
_deployment_put_payload.add_argument('start_ts',
                            type=lambda d: datetime.strptime(d, '%Y-%m-%dT%H:%M:%S.%fZ'),
                            help="The start date/time for the deployment."
                            )
_deployment_put_payload.add_argument('stop_ts',
                            type=lambda d: datetime.strptime(d, '%Y-%m-%dT%H:%M:%S.%fZ'),
                            help="The stop date/time for the deployment."
                            )
_deployment_put_payload.add_argument('disabled',
                            type=bool,
                            help="Is the deployment currently disabled."
                            )


@socketio.on('connect', namespace="/deployments")
def connect():
    print('client connected to deployments namespace')

@socketio.on('disconnect', namespace="/deployments")
def disconnect():
    print('client disconnected from deployments namespace')

@socketio.on('deployment_updated')
def handle_new_deployment(deployment):
    print('received new deployment ' + json.dumps(deployment.json()))
    emit('deployment_updated', deployment.json(), broadcast=True, namespace='/deployments')


@api.route('/deployment/<deployment_id>')
@api.param('deployment_id', 'The deployment identifier')
class Deployment(Resource):

    @classmethod
    @api.doc('get_deployment')
    @api.marshal_with(deploymentModel, 'Success', code=200)
    def get(cls, deployment_id: int):
        """
        Retrieve an deployment definition based on the definition's id.

        Must set the contents of the 'Authorization' header key/value to 'Bearer <access_token>
        where <access_token> is the token for an admin-level user.
        """
        deployment = DeploymentModel.find_by_id(deployment_id)
        if deployment:
            return deployment.json()
        raise NotFound('Deployment not found')

    @classmethod
    @api.doc('update_deployment')
    @api.expect(_deployment_put_payload)
    @api.response(204, 'Resource Updated')
    def put(cls, deployment_id: int):
        """
        Update an deployment definition based on the definition's id.

        Must set the contents of the 'Authorization' header key/value to 'Bearer <access_token>
        where <access_token> is the token for an admin-level user.
        """

        data = _deployment_put_payload.parse_args()

        deployment = DeploymentModel.find_by_id(deployment_id)

        if deployment:
            if data['name']:
                deployment.name = data['name']
            if data['start_ts']:
                deployment.start_ts = data['start_ts']
            if data['stop_ts']:
                deployment.stop_ts = data['stop_ts']
            if data['platform_id']:
                deployment.platform_id = data['platform_id']
            if data['disabled']:
                deployment.disabled = data['disabled']

        else:
            raise NotFound('Deployment does not exist.')

        try:
            deployment.save_to_db()
            handle_new_deployment(deployment)
        except Exception as error:
            print(error)
            raise InternalServerError("An error occurred saving to database.")

        return None, 204

    @api.doc('delete_deployment')
    @api.response(200, 'Success')
    def delete(self, deployment_id: int):
        """
        Delete an deployment definition based on the definition's id.

        Must set the contents of the 'Authorization' header key/value to 'Bearer <access_token>
        where <access_token> is the token for an admin-level user.
        """

        deployment = DeploymentModel.find_by_id(deployment_id)
        if deployment:
            try:
                deployment.delete_from_db()
            except Exception as error:
                print(error)
                raise InternalServerError("An error occurred saving to database.")

        return {'message': 'Deployment deleted'}, 200

@api.route('/deployment')
class DeploymentCreate(Resource):

    @classmethod
    @api.doc('create_deployment')
    @api.expect(_deployment_post_payload)
    @api.response(201, 'Resource Created')
    def post(cls):
        """
        Create a new deployment definition.

        Must set the contents of the 'Authorization' header key/value to 'Bearer <access_token>
        where <access_token> is the token for an admin-level user.
        """

        data = _deployment_post_payload.parse_args()

        platform = PlatformModel.find_by_id(data['platform_id'])
        if not platform:
            raise BadRequest("Plaform does not exist")

        if platform.platform_type == 1:
            raise BadRequest("Deployments can not be created for platform type = 1")

        if DeploymentModel.find_by_name(data['name']):
            raise BadRequest("A deployment with name '{}' already exists.".format(data['name']))

        deployment = DeploymentModel.find_by_platform_id(data['platform_id'])
        if deployment:
            deployment.name = data['name']
            deployment.start_ts = data['start_ts']
            deployment.stop_ts = data['stop_ts']
            deployment.platform_id = data['platform_id']
            deployment.disabled = data['disabled']
        else:
            deployment = DeploymentModel(**data)

        try:
            deployment.save_to_db()
            handle_new_deployment(deployment)
        except Exception as error:
            print(error)
            raise InternalServerError("An error occurred saving to database.")

        return {"message": "Deployment created successfully."}, 201

@api.route('/deployments')
class DeploymentList(Resource):
    @api.doc('get_deployment_list')
    @api.marshal_with(deploymentListModel, 'Success', code=200, skip_none=True)
    def get(self):
        """
        Retrieve the list of deployment definitions.

        Must set the contents of the 'Authorization' header key/value to 'Bearer <access_token>
        where <access_token> is the token for an admin-level user.
        """

        deployments = DeploymentModel.find_all()
        if len(deployments) == 0:
            raise NotFound("No deployments found")

        return {'deployments': [deployment.json() for deployment in deployments]}, 200
