from config import config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(confing_name):
    app = Flask(__name__)
    app.config.from_object(config[confing_name])
    config[confing_name].init_app(app)
    db.init_app(app)

    from .core import core as core_view
    app.register_blueprint(core_view)

    return app