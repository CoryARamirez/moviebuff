import os

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'asdfasdfasdf'
    SQLALCHEMY_DATABASE_URI = os.environ.['DATABASE_URL']