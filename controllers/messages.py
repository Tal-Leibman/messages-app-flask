import logging

from flask import Blueprint
from sqlalchemy.orm import Session

from db import mysql_client_instance, User, Message, MessageResponse

log = logging.getLogger(__name__)
messages_bp = Blueprint("messages", __name__)


@messages_bp.route("/write", methods=["POST"])
def write_message():
    pass


@messages_bp.route("/read/<user_id>", methods=["GET"])
def read_message(user_id: str):
    with mysql_client_instance.session_scope() as s:
        s: Session
        message = (
            s.query(Message)
            .with_for_update()
            .filter(Message.is_read == 0, Message.receiver_id == user_id)
            .order_by(Message.timestamp)
            .first()
        )
        if message is None:
            return {"status": "no unread messages to send"}
        from_user: User = s.query(User).filter(id=message.sender_id).first()
        message: Message
        message.is_read = 1

        response = MessageResponse(
            sent_from=from_user.email,
            subject=message.subject,
            body=message.body,
            timestamp=message.timestamp,
        )
    return response.to_json()
