from uuid import uuid4

from flask import Blueprint, request, abort
from sqlalchemy.orm import Session

from db import sql_client_instance, User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    validate_request_body(request.json)
    with sql_client_instance.session_scope() as s:
        s: Session
        user = s.query(User).filter(User.email == request.json["email"]).first()
        if user:
            return abort(400)
        new_user = User(email=request.json["email"])
        new_user.password = request.json["password"]
        token = str(uuid4())
        new_user.auth_token = token
        s.add(new_user)

    return {"status": "ok", "auth_token": token}


@auth_bp.route("/login", methods=["POST"])
def login():
    validate_request_body(request.json)
    with sql_client_instance.session_scope() as s:
        s: Session
        user = s.query(User).filter(User.email == request.json["email"]).first()
        if user is None:
            abort(403)
        user: User
        if user.validate_password(request.json["password"]):
            token = str(uuid4())
            user.auth_token = token
        else:
            abort(403)

    return {"status": "ok", "auth_token": token}

def validate_request_body(body:dict):
    if "email" not in body or "password" not in body:
        abort(400, "body must contain password and email")

