from .. import db

class DeploymentModel(db.Model):
    __tablename__ = 'deployments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    start_ts = db.Column(db.DateTime)
    stop_ts = db.Column(db.DateTime)
    platform_id = db.Column(db.Integer)
    disabled = db.Column(db.Boolean)

    def __init__(self, name, start_ts, stop_ts, platform_id, disabled):
        self.name = name
        self.start_ts = start_ts
        self.stop_ts = stop_ts
        self.platform_id = platform_id
        self.disabled = disabled

    def json(self):

        return {
            'id': self.id,
            'name': self.name,
            'start_ts': self.start_ts.isoformat(),
            'stop_ts': self.stop_ts.isoformat(),
            'platform_id': self.platform_id,
            'disabled': self.disabled,
        }

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()
    
    @classmethod
    def find_by_id(cls, deployment_id):
        return cls.query.filter_by(id=deployment_id).first()

    @classmethod
    def find_by_platform_id(cls, platform_id):
        return cls.query.filter_by(platform_id=platform_id).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
