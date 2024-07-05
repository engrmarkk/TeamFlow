from config import config_obj
from endpoints import auth as authentication_blueprint
from flask import Flask
from extensions import db, migrate, jwt, cors
from http_status  import HttpStatus
from utils import return_response
from status_res import StatusRes


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
                               message="Not Found", data={})

    # handle 500
    @app.errorhandler(500)
    def server_error(error):
        return return_response(HttpStatus.INTERNAL_SERVER_ERROR, status=StatusRes.FAILED,
                               message="Network Error", data={})

    # register blueprints
    app.register_blueprint(authentication_blueprint, url_prefix='/api/v1')

    # load
    return app
