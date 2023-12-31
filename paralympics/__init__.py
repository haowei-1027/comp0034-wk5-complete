import os
import logging
from pathlib import Path

import csv
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
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, 'paralympics.sqlite'),
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

    # Configure logging first
    configure_logging(app)

    # Log events to the logger
    app.logger.debug(f"Using Database: {app.config.get('SQLALCHEMY_DATABASE_URI')}")

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
        add_data_from_csv()

        # Register the routes and custom error handlers with the app in the context
        from paralympics import routes, error_handlers

    return app


def add_data_from_csv():
    """Adds data to the database if it does not already exist."""

    # Add import here and not at the top of the file to avoid circular import issues
    from paralympics.models import Region, Event

    # If there are no regions in the database, then add them
    first_region = db.session.execute(db.select(Region)).first()
    if not first_region:
        noc_file = Path(__file__).parent.parent.joinpath("data", "noc_regions.csv")
        with open(noc_file, 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header row
            for row in csv_reader:
                # row[0] is the first column, row[1] is the second column
                r = Region(NOC=row[0], region=row[1], notes=row[2])
                db.session.add(r)
            db.session.commit()

    # If there are no Events, then add them
    first_event = db.session.execute(db.select(Event)).first()
    if not first_event:
        event_file = Path(__file__).parent.parent.joinpath("data", "paralympic_events.csv")
        with open(event_file, 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header row
            for row in csv_reader:
                # row[0] is the first column, row[1] is the second column etc
                # type0,year1,country2,host3,NOC4,start5,end6,duration7,disabilities_included8,countries9,events10,
                # sports11,participants_m12,participants_f13,participants14,highlights15
                e = Event(type=row[0],
                          year=row[1],
                          country=row[2],
                          host=row[3],
                          NOC=row[4],
                          start=row[5],
                          end=row[6],
                          duration=row[7],
                          disabilities_included=row[8],
                          countries=row[9],
                          events=row[10],
                          sports=row[11],
                          participants_m=row[12],
                          participants_f=row[13],
                          participants=row[14],
                          highlights=row[15])
                db.session.add(e)
            db.session.commit()


def configure_logging(app):
    """ Configures Flask logging to a file.

    Logging level is set to DEBUG when testing which generates more detail.
    """
    logging.basicConfig(format='[%(asctime)s] %(levelname)s %(name)s: %(message)s')
    if app.config['TESTING']:
        logging.getLogger().setLevel(logging.DEBUG)
        handler = logging.FileHandler('paralympics_tests.log')  # Log to a file
    else:
        logging.getLogger().setLevel(logging.INFO)
        handler = logging.FileHandler('paralympics.log')  # Log to a file
    app.logger.addHandler(handler)
