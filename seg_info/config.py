import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'p9Bv<3Eid9%$i01'
    SQLALCHEMY_DATABASE_URI = 'mysql://dt_admin:admin2021@localhost/seginfo_db'


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
