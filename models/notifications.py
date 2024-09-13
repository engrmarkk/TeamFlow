from extensions import db
from sqlalchemy.orm import relationship
from utils import gen_uuid
from datetime import datetime


class Notifications(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.String(50), primary_key=True, default=gen_uuid)
    message = db.Column(db.Text, nullable=False)
    date_sent = db.Column(db.DateTime, default=datetime.now())
    recipient_id = db.Column(db.String(50), db.ForeignKey("users.id"), nullable=False)
    read = db.Column(db.Boolean, default=False)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def __repr__(self):
        return "<Notifications %r>" % self.message
