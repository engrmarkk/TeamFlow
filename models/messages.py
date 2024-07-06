from extensions import db
from sqlalchemy.orm import relationship
from utils import gen_uuid
from datetime import datetime


class Messages(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.String(50), primary_key=True, default=gen_uuid)
    content = db.Column(db.Text, nullable=False)
    date_sent = db.Column(db.DateTime, default=datetime.now())
    author_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.String(50), db.ForeignKey('projects.id'))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def __repr__(self):
        return '<Message %r>' % self.content