from flask import jsonify
from datetime import datetime, timedelta

from server import create_app, db, socketio

from server.models.deployment import DeploymentModel

app = create_app()

@app.before_first_request
def create_tables():
    db.create_all()

    """
    Init Deployment Table if empty
    """
    deployments = DeploymentModel.find_all()
    if not deployments:
        print('Populating deployments...')
        # DeploymentModel(name)
        DefaultDeployment = DeploymentModel('ROV-001')
        with app.app_context():
            db.session.add(DefaultDeployment)
            db.session.commit()

if __name__ == "__main__":

    socketio.run(app, port=5000, debug=True)
