import os

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import DeclarativeBase


# https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/quickstart/
class Base(DeclarativeBase):
    pass


def handle_404_error(e):
    """ Error handler for 404.

        Used when abort() is called. THe custom message is provided by the 'description=' parameter in abort().
        Args:
            HTTP 404 error

        Returns:
            JSON response with the validation error message and the 404 status code
        """
    return jsonify(error=str(e)), 404


# First create the db object using the SQLAlchemy constructor.
# Pass a subclass of either DeclarativeBase or DeclarativeBaseNoMeta to the constructor.
db = SQLAlchemy(model_class=Base)

# Create the Marshmallow instance after SQLAlchemy
# See https://flask-marshmallow.readthedocs.io/en/latest/#optional-flask-sqlalchemy-integration
ma = Marshmallow()


def create_app(test_config=None):
    # create and configure the app
    app = Flask('paralympics', instance_relative_config=True)

    app.config.from_mapping(
        # Generate your own SECRET_KEY using python secrets
        SECRET_KEY='l-tirPCf1S44mWAGoWqWlA',
        # configure the SQLite database, relative to the app instance folder
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, 'paralympics.sqlite')
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Configure logging
    from paralympics.utils import configure_logging
    configure_logging(app)

    # Register the custom 404 error handler that is defined in this python file
    app.register_error_handler(401, handle_404_error)

    # Initialise Flask with the SQLAlchemy database extension
    db.init_app(app)

    # Initialise Flask with the Marshmallow extension
    ma.init_app(app)

    # Models are defined in the models module, so you must import them before calling create_all, otherwise SQLAlchemy
    # will not know about them.
    from paralympics.models import User, Region, Event
    # Create the tables in the database
    # create_all does not update tables if they are already in the database.
    with app.app_context():
        db.create_all()

        from paralympics.utils import add_data
        add_data(db)

        # Register the routes and custom error handlers with the app in the context
        from paralympics import routes, error_handlers

    return app
