from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.debug = True

    return app


app = create_app()

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from website.models import Counts

