from extensions import db
from sqlalchemy.orm import relationship
from utils import gen_uuid
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from .projects import Projects


class Tasks(db.Model):
    id = db.Column(db.String(50), primary_key=True, default=gen_uuid)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=False, default="To Do")
    project_id = db.Column(db.String(50), db.ForeignKey('projects.id'), nullable=False)
    assignee_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=True)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.now())
    due_date = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        task = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'project_id': self.project_id,
            'assignee_id': self.assignee_id,
            'project_details': {
                'id': self.project.id,
                'name': self.project.name,
                'description': self.project.description,
                'created_by': f"{self.project.users.first_name.title()} {self.project.users.last_name.title()}",
                'date_created': self.project.date_created.strftime("%d %b, %Y")
            },
            'assigned_to': f"{self.assignee.last_name.title()} {self.assignee.first_name.title()}",
            'date_created': self.date_created,
            'due_date': self.due_date.strftime("%d %b, %Y"),
            'completed': self.completed
        }

        # add completed_at if completed
        if self.completed:
            task['completed_at'] = self.completed_at.strftime("%d %b, %Y")
        return task

    def to_dict2(self):
        task = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'project_id': self.project_id,
            'assignee_id': self.assignee_id,
            'assigned_to': f"{self.assignee.last_name.title()} {self.assignee.first_name.title()}",
            'date_created': self.date_created,
            'due_date': self.due_date.strftime("%d %b, %Y"),
            'completed': self.completed
        }

        # add completed_at if completed
        if self.completed:
            task['completed_at'] = self.completed_at.strftime("%d %b, %Y")
        return task

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return '<Tasks %r>' % self.title


def create_task(title, description, status, project_id, assignee_id, due_date):
    try:
        task = Tasks(title=title, description=description, status=status or "To Do", project_id=project_id,
                     assignee_id=assignee_id, due_date=due_date)
        task.save()
        return task
    except IntegrityError as e:
        print(e, "error@tasks/create-task")
        return None


def update_task(task_id, title, description, status, project_id, assignee_id, due_date):
    task = get_task(task_id, project_id)
    if task:
        task.title = title or task.title
        task.description = description or task.description
        task.status = status or task.status
        task.project_id = project_id or task.project_id
        task.assignee_id = assignee_id or task.assignee_id
        task.due_date = due_date or task.due_date
        task.completed = not task.completed if status == "Completed" else task.completed
        task.completed_at = datetime.now() if status == "Completed" else None
        task.update()
        return task
    return None


def get_task_for_project(project_id):
    return Tasks.query.filter_by(project_id=project_id).all()


# get a task by id
def get_task(task_id, project_id):
    return Tasks.query.filter_by(id=task_id, project_id=project_id).first()


def task_assigned_to_user(user_id):
    tasks = Tasks.query.filter_by(assignee_id=user_id).order_by(
        Tasks.date_created.desc()
    ).limit(10).all()
    all_tasks = [task.to_dict() for task in tasks]
    return all_tasks


def get_one_task(task_id, org_id):
    task = Tasks.query.join(Projects, Tasks.project_id == Projects.id).filter(
        Tasks.id == task_id, Projects.organization_id == org_id).first()
    if not task:
        return None
    return task


def get_users_tasks_for_project(project_id):
    tasks = Tasks.query.filter_by(project_id=project_id).all()
    users = [task.assignee.to_dict() for task in tasks if task.assignee is not None]
    return users


def statistics(user_id):
    total_tasks = Tasks.query.filter_by(assignee_id=user_id).count()
    completed_tasks = Tasks.query.filter_by(assignee_id=user_id, completed=True).count()
    not_started_tasks = Tasks.query.filter_by(assignee_id=user_id, status="To Do").count()
    in_progress_tasks = Tasks.query.filter_by(assignee_id=user_id, status="In Progress").count()
    return total_tasks, completed_tasks, not_started_tasks, in_progress_tasks
