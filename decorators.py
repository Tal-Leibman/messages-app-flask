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
        user = User.get_by_token(auth_token)
        if user is None:
            return abort(403)
        return func(user=user, *args, **kwargs)

    return wrapper


def validate_email_password(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "email" not in request.json or "password" not in request.json:
            abort(400, "body must contain password and email")
        user = User.get_by_email(request.json["email"])
        return func(user=user, *args, **kwargs)

    return wrapper
