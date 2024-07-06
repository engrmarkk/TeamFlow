from extensions import db
from sqlalchemy.orm import relationship
from utils import gen_uuid
from datetime import datetime


class Documents(db.Model):
    id = db.Column(db.String(50), primary_key=True, default=gen_uuid)
    name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    project_id = db.Column(db.String(50), db.ForeignKey('projects.id'), nullable=False)
    uploaded_by = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    uploaded_date = db.Column(db.DateTime, default=datetime.now())

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def __repr__(self):
        return '<Documents %r>' % self.name
