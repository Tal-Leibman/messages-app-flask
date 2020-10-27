from typing import Literal

from flask import Blueprint, abort, request
from flask import current_app

from decorators import auth_required
from models import (
    User,
    Message,
    MessageResponse,
    ParseWriteMessageRequest,
    MessageFetchRequestStatus,
    MessagesUsers,
)
from models import db

messages_bp = Blueprint("messages", __name__)


@messages_bp.route("/write", methods=["POST"])
@auth_required
def write_message(user: User):
    request_data = ParseWriteMessageRequest(**request.json)
    message_receiver = User.get_by_id(request_data.receiver_id)
    if message_receiver is None:
        abort(404, "message receiver not found")
    message = Message(
        body=request_data.body,
        subject=request_data.subject,
        sender=user,
        receiver=message_receiver,
    )
    db.session.add(message)
    db.session.flush()
    for _id in (user.id, message_receiver.id):
        db.session.add(MessagesUsers(message_id=message.id, viewer_id=_id))
    db.session.commit()
    return {"status": "ok"}


@messages_bp.route("/read", methods=["GET"])
@auth_required
def read_message(user: User):
    msg = (
        user.messages(status=MessageFetchRequestStatus.all_unread, inbox_outbox="inbox")
        .order_by(Message.timestamp)
        .first()
    )
    if msg is None:
        return {"status": f"no unread messages for {user.email=}"}
    msg: MessagesUsers
    msg.message.is_read = True
    db.session.commit()
    response = MessageResponse(
        message_id=msg.message_id,
        sent_from=msg.message.sender.email,
        subject=msg.message.subject,
        body=msg.message.body,
        timestamp=msg.message.timestamp,
    )
    return response.to_json()


@messages_bp.route("/<status>/<inbox_outbox>", methods=["GET"])
@auth_required
def get_messages(user: User, status: str, inbox_outbox: Literal["inbox", "outbox"]):
    """
    to use pagination send query params page and per_page
    """
    try:
        status = MessageFetchRequestStatus(status)
    except ValueError:
        abort(
            400,
            f"Provided {status=} invalid, use {[_status.value for _status in MessageFetchRequestStatus]}",
        )

    messages_query = user.messages(status, inbox_outbox)
    max_per_page = current_app.config["MAX_MESSAGES_FETCH_COUNT"]
    messages = (
        messages_query.order_by(Message.timestamp)
        .paginate(max_per_page=max_per_page, error_out=False)
        .items
    )
    m: MessagesUsers
    messages_response = [
        MessageResponse(
            message_id=m.message_id,
            sent_from=m.message.sender.email,
            subject=m.message.subject,
            body=m.message.body,
            timestamp=m.message.timestamp,
        )
        for m in messages
    ]
    return {"status": "ok", "messages": messages_response}


@messages_bp.route("/<message_id>", methods=["DELETE"])
@auth_required
def delete_message(user: User, message_id: str):
    message = MessagesUsers.get_by_viewer_id(user.id, message_id)
    if message is None:
        return {"status": f"no message found  {message_id=} and {user.email=}"}
    db.session.delete(message)
    db.session.commit()
    return {"status": "ok"}
