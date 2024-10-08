from extensions import db
from sqlalchemy.orm import relationship
from utils import gen_uuid
from datetime import datetime


class Projects(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.String(50), primary_key=True, default=gen_uuid)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())
    owner_id = db.Column(db.String(50), db.ForeignKey("users.id"), nullable=False)
    organization_id = db.Column(
        db.String(50), db.ForeignKey("organizations.id"), nullable=True
    )
    tasks = relationship("Tasks", backref="project", lazy=True, cascade="all, delete")
    document = relationship("Documents", backref="project", lazy=True, cascade="all, delete")

    def to_dict(self):
        proj = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "date_created": self.date_created,
            "created_by": f"{self.users.last_name.title()} {self.users.first_name.title()}",
        }
        if self.tasks:
            proj["tasks"] = [task.to_dict2() for task in self.tasks]
        if self.document:
            proj["documents"] = [doc.to_dict() for doc in self.document]
        return proj

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<Projects %r>" % self.name


def create_project(name, description, owner_id, org_id):
    project = Projects(
        name=name, description=description, owner_id=owner_id, organization_id=org_id
    )
    project.save()
    return project


def update_project(project_id, name, description, org_id):
    project = Projects.query.filter_by(id=project_id, organization_id=org_id).first()
    if not project:
        return None
    project.name = name or project.name
    project.description = description or project.description
    project.update()
    return project


def get_one_project(project_id, org_id):
    return Projects.query.filter_by(id=project_id, organization_id=org_id).first()


def get_projects(org_id, page, per_page):
    projects = (
        Projects.query.filter_by(organization_id=org_id)
        .order_by(Projects.date_created.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    total_items = projects.total
    total_pages = projects.pages
    return projects, total_items, total_pages


def is_project_valid(project_id):
    return Projects.query.filter_by(id=project_id).first()
