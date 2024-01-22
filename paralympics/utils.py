# Helper classes
import csv
from pathlib import Path
import logging

from paralympics.models import Region, Event


def add_data(db):
    """Adds data to the database if it does not already exist.

    This method uses db which is the FlaskSQLALchemy instance for the app

    :param db: SQLAlchemy database for the app
    """

    # If there are no regions in the database, then add them
    first_region = db.session.execute(db.select(Region)).first()
    if not first_region:
        print("Start adding region data to the database")
        region_file = Path(__file__).parent.parent.joinpath("data", "noc_regions.csv")
        with open(region_file, 'r') as file:
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
                e = Event(type=row[0],
                          year=row[1],
                          country=row[2],
                          host=row[3],
                          NOC=row[4],
                          start=row[5],
                          end=row[6],
                          duration=row[7] or None,
                          disabilities_included=row[8],
                          countries=row[9] or None,
                          events=row[10] or None,
                          sports=row[11] or None,
                          participants_m=row[12] or None,
                          participants_f=row[13] or None,
                          participants=row[14] or None,
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
