from config import config_obj
from endpoints import auth as authentication_blueprint, account as account_blueprint
from flask import Flask
from extensions import db, migrate, jwt, cors
from http_status import HttpStatus
from utils import return_response
from status_res import StatusRes
from models import Users, user_project, Projects, Messages, Notifications, Documents, Tasks


def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_obj[config_name])
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)

    # handle 404
    @app.errorhandler(404)
    def not_found(error):
        return return_response(HttpStatus.NOT_FOUND, status=StatusRes.FAILED,
                               message="Not Found")

    # handle 500
    @app.errorhandler(500)
    def server_error(error):
        return return_response(HttpStatus.INTERNAL_SERVER_ERROR, status=StatusRes.FAILED,
                               message="Network Error")

    @app.errorhandler(405)
    def method_not_allowed(error):
        return return_response(HttpStatus.METHOD_NOT_ALLOWED, status=StatusRes.FAILED,
                               message="Method Not Allowed")

    # function tha returns the current user
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user

    # function that validates the current user
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        user = Users.query.filter_by(id=identity).one_or_none()
        return user

    # shell context
    @app.shell_context_processor
    def shell_context():
        return {
            'db': db,
            'Users': Users,
            'user_project': user_project,
            'Projects': Projects,
            'Messages': Messages,
            'Notifications': Notifications,
            'Documents': Documents,
            'Tasks': Tasks
        }

    # register blueprints
    app.register_blueprint(authentication_blueprint, url_prefix='/api/v1')
    app.register_blueprint(account_blueprint, url_prefix='/api/v1')

    # load
    return app
