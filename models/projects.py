from extensions import db
from sqlalchemy.orm import relationship
from utils import gen_uuid
from datetime import datetime


class Projects(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.String(50), primary_key=True, default=gen_uuid)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())
    owner_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    organization_id = db.Column(db.String(50), db.ForeignKey('organizations.id'), nullable=True)
    users = relationship('Users', secondary='users_project', back_populates='projects')
    tasks = relationship('Tasks', backref='project', lazy=True)
    document = relationship('Documents', backref='project', lazy=True)

    def to_dict(self):
        proj = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'date_created': self.date_created,
            'owner_id': self.owner_id
        }
        if self.tasks:
            proj['tasks'] = [task.to_dict() for task in self.tasks]
        return proj

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def __repr__(self):
        return '<Projects %r>' % self.name


def create_project(name, description, owner_id):
    project = Projects(name=name, description=description, owner_id=owner_id)
    project.save()
    return project


def get_one_project(project_id, org_id):
    return Projects.query.filter_by(id=project_id, organization_id=org_id).first()


def get_projects(org_id):
    return Projects.query.filter_by(organization_id=org_id).order_by(Projects.date_created.desc()
                                                                     ).all()
