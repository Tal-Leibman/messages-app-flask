from functools import wraps

from flask import request, abort
from sqlalchemy.orm import Session

from db import sql_client_instance, User


def auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_token = request.headers.get("Authorization", None)
        if auth_token is None:
            abort(400, "missing Authorization header")
        with sql_client_instance.session_scope() as s:
            s: Session
            user = s.query(User).filter(auth_token == User.auth_token).first()
            if user is None:
                abort(403)
            user_id = user.id
        return func(user_id=user_id, *args, **kwargs)

    return wrapper
