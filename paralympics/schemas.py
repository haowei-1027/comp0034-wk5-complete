"""
Schemas for each of the models in the paralympics app.
"""
from paralympics.models import Event, Region, User
from paralympics import db, ma


# Flask-Marshmallow Schemas

class RegionSchema(ma.SQLAlchemySchema):
    """Marshmallow schema defining the attributes for creating a new region."""

    class Meta:
        model = Region
        load_instance = True
        sqla_session = db.session
        include_relationships = True

    NOC = ma.auto_field()
    region = ma.auto_field()
    notes = ma.auto_field()


class EventSchema(ma.SQLAlchemyAutoSchema):
    """Marshmallow schema for the attributes of an event class. Inherits all the attributes from the Event class."""

    class Meta:
        model = Event
        include_fk = True
        # load_instance = True creates an object from .load() instead of a dictionary
        load_instance = True
        sqla_session = db.session
        include_relationships = True


class UserSchema(ma.SQLAlchemySchema):
    """Marshmallow schema defining the attributes for creating a new user.

    The password_hash is set later using the
    """

    class Meta:
        model = User
        load_instance = True
        sqla_session = db.session
        include_relationships = True

    email = ma.auto_field()
    password_hash = ma.auto_field()
