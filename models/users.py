from extensions import db
from sqlalchemy.orm import relationship
from utils import gen_uuid, generate_otp, generate_random_string
from datetime import datetime, timedelta
from passlib.hash import pbkdf2_sha256 as hasher


class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(50), primary_key=True, default=gen_uuid)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.now())
    email_verified = db.Column(db.Boolean, default=False)
    projects = relationship('Projects', secondary='users_project', back_populates='users')
    tasks = relationship('Tasks', backref='assignee', lazy=True)
    messages = relationship('Messages', backref='author', lazy=True)
    notifications = relationship('Notifications', backref='recipient', lazy=True)
    usersession = relationship('UserSession', backref='user', lazy=True, uselist=False)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def __repr__(self):
        return '<Users %r>' % self.username


# otp session
class UserSession(db.Model):
    __tablename__ = 'user_session'

    id = db.Column(db.String(50), primary_key=True, default=gen_uuid)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    reset_p = db.Column(db.String(50), nullable=True)
    otp = db.Column(db.String(6), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)
    reset_p_expiry = db.Column(db.DateTime, nullable=True)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()


# check if email exist and password is correct
def authenticate(email, password):
    user = Users.query.filter_by(email=email).first()
    if user and hasher.verify(password, user.password):
        return user
    return None


# validate email
def email_exist(email):
    user = Users.query.filter_by(email=email).first()
    if user:
        return True
    return False


# validate username
def username_exist(username):
    user = Users.query.filter_by(username=username).first()
    if user:
        return True
    return False


def create_user(first_name, last_name, username, email, password):
    user = Users(first_name=first_name, last_name=last_name, username=username, email=email, password=hasher.hash(password))
    user.save()
    return user


def create_otp(user_id):
    # expiry time is 10 minutes
    expiry = datetime.now() + timedelta(minutes=10)
    otp = generate_otp()
    usersession = UserSession.query.filter_by(user_id=user_id).first()
    if usersession:
        usersession.otp = otp
        usersession.otp_expiry = expiry
        usersession.update()
    else:
        usersession = UserSession(user_id=user_id, otp=otp, otp_expiry=expiry)
        usersession.save()
    return usersession


def create_reset_p(user_id):
    # expiry time is 10 minutes
    expiry = datetime.now() + timedelta(minutes=10)
    reset_p = f"ly{generate_random_string()}"
    usersession = UserSession.query.filter_by(user_id=user_id).first()
    if usersession:
        usersession.reset_p = reset_p
        usersession.reset_p_expiry = expiry
        usersession.update()
    else:
        usersession = UserSession(user_id=user_id, reset_p=reset_p, reset_p_expiry=expiry)
        usersession.save()
    return usersession


def get_user_by_email(email):
    return Users.query.filter_by(email=email).first()


def get_user_by_reset_p(reset_p):
    usersession = UserSession.query.filter_by(reset_p=reset_p).first()
    return usersession


def update_password(user, password):
    user.password = hasher.hash(password)
    user.update()

    return user


def current_user_info(user):
    return {
        "id": user.id,
        "first_name": user.first_name.title(),
        "last_name": user.last_name.title(),
        "username": user.username,
        "email": user.email
    }
