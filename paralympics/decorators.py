from functools import wraps
import jwt
from flask import request, make_response, current_app as app
from paralympics import db
from paralympics.models import User


def token_required(f):
    """Require valid jwt for a route

    Decorator to protect routes using jwt
    """

    @wraps(f)
    def decorator(*args, **kwargs):
        token = None

        # See if there is an Authorization section in the HTTP request headers
        if 'Authorization' in request.headers:
            token = request.headers.get("Authorization")

        # If not, then return a 401 error (missing or invalid authentication credentials)
        if not token:
            response = {"message": "Authentication Token missing"}
            return make_response(response, 401)
        # Check the token is valid and find the user in the database using their email address
        try:
            # Use PyJWT.decode(token, key, algorithms) to decode the token with the public key for the app
            # See https://pyjwt.readthedocs.io/en/latest/api.html
            app.logger.debug(f' Token before decode {token}')
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            # Find the user in the database using their email address which is in the data of the decoded token
            current_user = db.session.execute(
                db.select(User).filter_by(id=data.get("user_id"))
            ).scalar_one_or_none()
        # If the email is not found, the token is likely invalid so return 401 error
        except:
            response = {"message": "Token invalid"}
            return make_response(response, 401)

        # If successful, return the user information attached to the token
        return f(current_user, *args, **kwargs)

    return decorator
