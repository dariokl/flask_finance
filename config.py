import os
from dotenv import load_dotenv

load_dotenv()

#used to create SQLite db for development
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """ The main config class required setup in .env type of file make sure you delete all the or statements
    adding send grind would be the best option to handle the daily email flow"""
    #Mail setup
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    @staticmethod
    def init_app(app):
        pass

class ProductionConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI= 'mysql+pymysql://{user}:{pw}@{url}/{db}'.format(user=os.environ.get('MYSQL_USER'),\
                                                                                    pw=os.environ.get('MYSQL_PW'),\
                                                                                    url=os.environ.get('MYSQL_URL'),\
                                                                                    db=os.environ.get('MYSQL_DB'))


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'dev-database.sqlite')

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}