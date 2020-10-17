import logging
from flask import Blueprint, request, abort
from sqlalchemy.orm import Session
from uuid import uuid4

from db import sql_client_instance, User

log = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    request_body = request.json
    if "email" not in request_body or "password" not in request_body:
        abort(400, "body must contain password and email")
    with sql_client_instance.session_scope() as s:
        s: Session
        user = s.query(User).filter(User.email == request_body["email"]).first()
        if user:
            return abort(400)
        new_user = User(email=request_body["email"])
        new_user.password = request_body["password"]
        token = str(uuid4())
        new_user.auth_token = token
        s.add(new_user)

    return {"status": "ok", "auth_token": token}


@auth_bp.route("/login", methods=["POST"])
def login():
    request_body = request.json
    if "email" not in request_body or "password" not in request_body:
        abort(400, "body must contain password and email")
    with sql_client_instance.session_scope() as s:
        s: Session
        user = s.query(User).filter(User.email == request_body["email"]).first()
        if user is None:
            abort(403)
        user: User
        if user.validate_password(request_body["password"]):
            token = str(uuid4())
            user.auth_token = token
        else:
            abort(403)

    return {"status": "ok", "auth_token": token}
