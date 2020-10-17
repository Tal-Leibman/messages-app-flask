import logging

from flask import Blueprint, request, abort
from sqlalchemy.orm import Session

from db import sql_client_instance, User

log = logging.getLogger(__name__)
users_bp = Blueprint("users", __name__)


@users_bp.route("/register", methods=["POST"])
def register():
    request_body = request.json
    with sql_client_instance.session_scope() as s:
        s: Session
        user = s.query(User).filter(User.email == request_body["email"]).first()
        if user:
            return abort(400)
        s.add((User(email=request_body["email"])))
    return {"status": "ok"}
