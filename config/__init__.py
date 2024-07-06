import os

base_dir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # jtw config
    JWT_SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    # expiring time
    JWT_ACCESS_TOKEN_EXPIRES = 3600


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(base_dir, 'teamflow.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


config_obj = {
    'development': DevelopmentConfig
}
