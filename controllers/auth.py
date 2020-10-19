from uuid import uuid4

from flask import Blueprint, request, abort

from decorators import auth_required, validate_email_password
from models import User, db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
@validate_email_password
def register(user: User):
    if user:
        return abort(403)
    new_user = User(email=request.json["email"])
    new_user.password = request.json["password"]
    token = str(uuid4())
    new_user.auth_token = token
    db.session.add(new_user)
    db.session.commit()
    return {"status": "ok", "auth_token": token, "user_id": new_user.id}


@auth_bp.route("/login", methods=["POST"])
@validate_email_password
def login(user: User):
    if user is None:
        abort(403)
    if user.validate_password(request.json["password"]):
        token = str(uuid4())
        user.auth_token = token
        db.session.commit()
        return {"status": "ok", "auth_token": token, "user_id": user.id}
    else:
        abort(403)


@auth_bp.route("/logout", methods=["DELETE"])
@auth_required
def logout(user: User):
    user.auth_token = None
    db.session.commit()
    return {"status": "ok"}
