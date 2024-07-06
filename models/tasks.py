from extensions import db
from sqlalchemy.orm import relationship
from utils import gen_uuid
from datetime import datetime


class Tasks(db.Model):
    id = db.Column(db.String(50), primary_key=True, default=gen_uuid)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=False, default="To Do")
    project_id = db.Column(db.String(50), db.ForeignKey('projects.id'), nullable=False)
    assignee_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.now())
    due_date = db.Column(db.DateTime, nullable=True)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def __repr__(self):
        return '<Tasks %r>' % self.title
