from functools import wraps

from flask import request, abort

from models import User


def auth_required(func):
    """
    check if a user has a valid Authorization header and return the wrapped function with the user.
    wrapped function must accept param user of type User
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_token = request.headers.get("Authorization", None)
        if auth_token is None:
            abort(400, "missing Authorization header")
        user = User.query.filter(auth_token == User.auth_token).first()
        if user is None:
            return abort(403)
        return func(user=user, *args, **kwargs)

    return wrapper
