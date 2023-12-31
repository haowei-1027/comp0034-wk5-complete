# Create database and import data from CSV to database table using sqlite3
from pathlib import Path
import sqlite3
import pandas as pd


def create_db():
    """Create SQLite database with data.

    Create the database outside the Flask application code. You then do not need `db.create_all()` and `add_data()`
    in the create_app() function.
    """

    # 1. Create a SQLite database engine that connects to the database file
    db_file = Path(__file__).parent.parent.joinpath("instance", "paralympics.sqlite")
    connection = sqlite3.connect(db_file)

    # 2. Create a cursor object to execute SQL queries
    cursor = connection.cursor()

    # 2. Define the tables in SQL
    # 'region' table definition in SQL
    create_region_table = """CREATE TABLE if not exists region(
                    NOC TEXT PRIMARY KEY,
                    region TEXT NOT NULL,
                    notes TEXT);
                    """

    # 'event' table definition in SQL
    create_event_table = """CREATE TABLE if not exists event(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        year INTEGER,
        country TEXT,
        host TEXT,
        NOC TEXT,
        start TEXT,
        end TEXT,
        duration INTEGER,
        disabilities_included TEXT,
        events INTEGER,
        sports INTEGER,
        countries INTEGER,
        participants_m INTEGER,
        participants_f INTEGER,
        participants INTEGER,
        highlights TEXT,
        FOREIGN KEY(NOC) REFERENCES region(NOC));"""

    # 4. Execute SQL to create the tables in the database
    cursor.execute(create_region_table)
    cursor.execute(create_event_table)

    # 5. Commit the changes to the database (this saves the tables created in the previous step)
    connection.commit()

    # 6. Import data from CSV to database table using pandas
    # Read the noc_regions data to a pandas dataframe
    na_values = ["", ]
    noc_file = Path(__file__).parent.joinpath("noc_regions.csv")
    noc_regions_df = pd.read_csv(noc_file, keep_default_na=False, na_values=na_values)

    # Read the paralympics event data to a pandas dataframe
    event_file = Path(__file__).parent.joinpath("paralympic_events.csv")
    paralympics_df = pd.read_csv(event_file)

    # 7. Write the pandas DataFrame contents to the database tables
    # For the region table we do not want the pandas DataFrame index column
    noc_regions_df.to_sql("region", connection, if_exists="append", index=False)
    # For the event table we want the pandas index, but it needs to start from 1 and not 0
    paralympics_df.index += 1
    paralympics_df.to_sql("event", connection, if_exists="append", index_label='id')

    # 8. Close the database connection
    connection.close()


if __name__ == '__main__':
    create_db()
