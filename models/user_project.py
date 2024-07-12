from extensions import db
from .projects import Projects

user_project = db.Table('users_project',
                        db.Column('user_id', db.String(50), db.ForeignKey('users.id'), primary_key=True),
                        db.Column('project_id', db.String(50), db.ForeignKey('projects.id'), primary_key=True)
                        )


# get user_ids
def get_user_ids_by_project_id(project_id):
    project = Projects.query.filter_by(id=project_id).first()
    return [user.id for user in project.users] if project else []
