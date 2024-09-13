from extensions import db
from sqlalchemy.orm import relationship
from utils import gen_uuid
from datetime import datetime
from .projects import Projects


class Messages(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.String(50), primary_key=True, default=gen_uuid)
    content = db.Column(db.Text, nullable=False)
    date_sent = db.Column(db.DateTime, default=datetime.now())
    author_id = db.Column(db.String(50), db.ForeignKey("users.id"), nullable=False)
    project_id = db.Column(db.String(50), db.ForeignKey("projects.id"))

    def to_dict(self, current_user_id=None):
        msgs = {
            "id": self.id,
            "content": self.content,
            "date_sent": self.date_sent.strftime("%d %b, %Y"),
            "author": f"{self.author.last_name.title()} {self.author.first_name.title()}",
            "project_id": self.project_id,
        }

        if current_user_id:
            msgs["is_author"] = current_user_id == self.author_id

        return msgs

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def __repr__(self):
        return "<Message %r>" % self.content


def create_message(content, author_id, project_id):
    message = Messages(content=content, author_id=author_id, project_id=project_id)
    message.save()
    return message


def get_messages(project_id, org_id):
    print("getting messages from db")
    messages = (
        Messages.query.join(Projects, Projects.organization_id == org_id)
        .filter(Messages.project_id == project_id)
        .order_by(Messages.date_sent.asc())
        .all()
    )

    return messages
