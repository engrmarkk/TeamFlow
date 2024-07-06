from extensions import db

user_project = db.Table('users_project',
                        db.Column('user_id', db.String(50), db.ForeignKey('users.id'), primary_key=True),
                        db.Column('project_id', db.String(50), db.ForeignKey('projects.id'), primary_key=True)
                        )
