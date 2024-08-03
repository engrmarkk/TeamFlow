import os

base_dir = os.path.abspath(os.path.dirname(__file__))

uri = f"""postgresql://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@{os.environ.get('POSTGRES_HOST')}:{os.environ.get('POSTGRES_PORT')}/{os.environ.get('POSTGRES_DB')}"""


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # jtw config
    JWT_SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    # expiring time
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    RESULT_BACKEND = f"redis://{os.environ.get('REDIS_HOST')}:{os.environ.get('REDIS_PORT')}"
    BROKER_URL = f"redis://{os.environ.get('REDIS_HOST')}:{os.environ.get('REDIS_PORT')}"


class DevelopmentConfig(Config):
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(base_dir, 'teamflow.sqlite')
    SQLALCHEMY_DATABASE_URI = uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"


config_obj = {
    'development': DevelopmentConfig,
    'testing': TestConfig
}
