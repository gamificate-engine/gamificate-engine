import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object): 
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['gamificate.engine@gmail.com']

    MONITORING_USERNAME = os.environ.get('MONITORING_USERNAME')
    MONITORING_PASSWORD = os.environ.get('MONITORING_PASSWORD')
    MONITORING_TOKEN = os.environ.get('MONITORING_TOKEN')
    MONITORING_DB = os.environ.get('MONITORING_DB')
    APP_VERSION = os.environ.get('APP_VERSION')

    BADGES_PER_PAGE = 12
    USERS_PER_PAGE = 12
    REWARDS_PER_PAGE = 12