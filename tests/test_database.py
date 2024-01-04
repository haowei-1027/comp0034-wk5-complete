# A test that includes using a context to check the database
from sqlalchemy import func
from paralympics import db
from paralympics.models import Region, User


def test_post_region_database_update(client, app):
    """
    GIVEN a Flask test client and test app
    AND valid JSON for a new region
    WHEN a POST request is made to /regions
    THEN the database should have one more entry
    """
    region_json = {"NOC": "ZBZ", "region": "ZedBeeZed"}

    # Count the rows in the Region table before and after the post
    with app.app_context():
        num_rows_start = db.session.scalar(db.select(func.count(Region.NOC)))
        client.post("/regions", json=region_json)
        num_rows_end = db.session.scalar(db.select(func.count(Region.NOC)))
    assert num_rows_end - num_rows_start == 1


def test_post_region_database_update_again(test_client):
    """
    GIVEN a Flask test client that has an application context
    AND valid JSON for a new region
    WHEN a POST request is made to /regions
    THEN the database should have one more entry
    """
    region_json = {"NOC": "ZUZ", "region": "ZedYouZed"}

    # Count the rows in the Region table before and after the post
    num_rows_start = db.session.scalar(db.select(func.count(Region.NOC)))
    test_client.post("/regions", json=region_json)
    num_rows_end = db.session.scalar(db.select(func.count(Region.NOC)))
    assert num_rows_end - num_rows_start == 1


# Test that doesn't make a request to a route
def test_database_after_insert(test_client, random_user_json):
    """
        GIVEN a test_client with an application context
        AND a new user
        WHEN a user is added to the database
        THEN the database User table should have one more entry
        """
    num_rows_start = db.session.scalar(db.select(func.count(User.id)))
    user = User(email=random_user_json['email'])
    user.set_password(random_user_json['password'])
    db.session.add(user)
    db.session.commit()
    num_rows_end = db.session.scalar(db.select(func.count(User.id)))
    assert num_rows_end - num_rows_start == 1
