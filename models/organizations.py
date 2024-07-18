from extensions import db
from sqlalchemy.orm import relationship
from utils import gen_uuid, generate_otp, generate_random_string
from datetime import datetime, timedelta


class Organizations(db.Model):
    __tablename__ = 'organizations'
    id = db.Column(db.String(50), primary_key=True, default=gen_uuid)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())
    users = relationship('Users', secondary='users_organization', back_populates='organizations')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'date_created': self.date_created
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def __repr__(self):
        return '<Organizations %r>' % self.name


def create_org(name, description):
    org = Organizations(name=name.lower(), description=description)
    org.save()
    return org.id


def check_if_org_exist(name):
    return Organizations.query.filter_by(name=name.lower()).first()
