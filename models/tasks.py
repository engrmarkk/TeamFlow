from extensions import db
from sqlalchemy.orm import relationship
from utils import gen_uuid
from datetime import datetime
from sqlalchemy.exc import IntegrityError


class Tasks(db.Model):
    id = db.Column(db.String(50), primary_key=True, default=gen_uuid)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=False, default="To Do")
    project_id = db.Column(db.String(50), db.ForeignKey('projects.id'), nullable=False)
    assignee_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.now())
    due_date = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'project_id': self.project_id,
            'assignee_id': self.assignee_id,
            'assigned_to': f"{self.assignee.last_name.title()} {self.assignee.first_name.title()}",
            'date_created': self.date_created,
            'due_date': self.due_date
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def __repr__(self):
        return '<Tasks %r>' % self.title


def create_task(title, description, status, project_id, assignee_id, due_date):
    try:
        task = Tasks(title=title, description=description, status=status if status else "To Do", project_id=project_id,
                     assignee_id=assignee_id, due_date=due_date)
        task.save()
        return task
    except IntegrityError as e:
        print(e, "error@tasks/create-task")
        return None


def get_task_for_project(project_id):
    return Tasks.query.filter_by(project_id=project_id).all()


# get a task by id
def get_task(task_id, project_id):
    return Tasks.query.filter_by(id=task_id, project_id=project_id).first()
