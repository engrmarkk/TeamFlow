from extensions import db
from sqlalchemy.orm import relationship
from utils import gen_uuid
from datetime import datetime


class Documents(db.Model):
    id = db.Column(db.String(50), primary_key=True, default=gen_uuid)
    name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    public_id = db.Column(db.String(255))  # This is cloudinary public id
    project_id = db.Column(db.String(50), db.ForeignKey("projects.id"), nullable=False)
    uploaded_by = db.Column(db.String(50), db.ForeignKey("users.id"), nullable=False)
    uploaded_date = db.Column(db.DateTime, default=datetime.now())

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "public_id": self.public_id,
            "project_id": self.project_id,
            "uploaded_by": f"{self.user.last_name} {self.user.first_name}",
            "uploaded_date": self.uploaded_date.strftime("%d-b-%Y, %H:%M:%S"),
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def __repr__(self):
        return "<Documents %r>" % self.name


# create document
def create_document(name, url, project_id, uploaded_by, public_id):
    document = Documents(
        name=name,
        url=url,
        project_id=project_id,
        uploaded_by=uploaded_by,
        public_id=public_id,
    )
    document.save()
    return document
