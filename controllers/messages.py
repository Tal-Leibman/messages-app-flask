import os
from operator import or_

from flask import Blueprint, abort, request

from decorators import auth_required
from models import (
    User,
    Message,
    MessageResponse,
    ParseWriteMessageRequest,
    MessageFetchRequestStatus,
)
from models import db

messages_bp = Blueprint("messages", __name__)
MAX_MESSAGES_FETCH_COUNT = int(os.getenv("MAX_MESSAGES_FETCH_COUNT", "5"))


@messages_bp.route("/write", methods=["POST"])
@auth_required
def write_message(user: User):
    request_data = ParseWriteMessageRequest(**request.json)
    message_receiver = User.get_by_id(request_data.receiver_id)
    if message_receiver is None:
        abort(404, "message receiver not found")
    db.session.add(
        Message(
            sender_id=user.id,
            receiver_id=message_receiver.id,
            body=request_data.body,
            subject=request_data.subject,
        )
    )
    db.session.commit()
    return {"status": "ok"}


@messages_bp.route("/read", methods=["GET"])
@auth_required
def read_message(user: User):
    message = (
        user.messages_received.filter(Message.is_read == False)
        .order_by(Message.timestamp)
        .first()
    )
    if message is None:
        return {"status": f"no unread messages for {user.email=}"}
    from_user = User.get_by_id(message.receiver_id)
    message: Message
    message.is_read = True
    db.session.commit()
    response = MessageResponse(
        message_id=message.id,
        sent_from=from_user.email,
        subject=message.subject,
        body=message.body,
        timestamp=message.timestamp,
    )
    return response.to_json()


@messages_bp.route("/<status>", methods=["GET"])
@auth_required
def get_messages(user: User, status: str):
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
    if status.value == MessageFetchRequestStatus.all_read.value:
        messages_query = user.messages_received.filter(Message.is_read == True)
    elif status.value == MessageFetchRequestStatus.all_unread.value:
        messages_query = user.messages_received.filter(Message.is_read == False)
    elif status.value == MessageFetchRequestStatus.all.value:
        messages_query = user.messages_received
    else:
        raise RuntimeError(
            "MessageFetchRequestStatus enum may have been changed received value"
        )
    messages = (
        messages_query.order_by(Message.timestamp)
        .paginate(max_per_page=MAX_MESSAGES_FETCH_COUNT, error_out=False)
        .items
    )
    messages_response = [
        MessageResponse(
            message_id=m.id,
            sent_from=m.sender.email,
            subject=m.subject,
            body=m.body,
            timestamp=m.timestamp,
        )
        for m in messages
    ]

    return {"status": "ok", "messages": messages_response}


@messages_bp.route("/<message_id>", methods=["DELETE"])
@auth_required
def delete_message(user: User, message_id: str):
    message = Message.query.filter(
        Message.id == message_id,
        or_(Message.receiver_id == user.id, Message.sender_id == user.id),
    ).first()
    if message is None:
        return {"status": f"no message found  {message_id=} and {user.email=}"}
    db.session.delete(message)
    db.session.commit()
    return {"status": "ok"}
