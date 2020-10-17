from operator import or_

from flask import Blueprint, abort, request
from sqlalchemy.orm import Session

from auth_decorator import auth_required
from db import (
    sql_client_instance,
    User,
    Message,
    MessageResponse,
    ParseWriteMessageRequest,
    MessageFetchRequestStatus,
)

messages_bp = Blueprint("messages", __name__)


@messages_bp.route("/write/<user_id>", methods=["POST"])
@auth_required
def write_message(user_id: str):
    with sql_client_instance.session_scope() as s:
        s: Session
        current_user = User.find_by_id(s, user_id)
        if current_user is None:
            abort(404, "message sender not found")
        request_data = ParseWriteMessageRequest(**request.json)
        message_receiver: User = s.query(User).filter(
            User.id == request_data.receiver_id
        ).first()
        if message_receiver is None:
            abort(404, "message receiver not found")
        s.add(
            Message(
                sender_id=current_user.id,
                receiver_id=message_receiver.id,
                body=request_data.body,
                subject=request_data.subject,
            )
        )
    return {"status": "ok"}


@messages_bp.route("/read/<user_id>", methods=["GET"])
@auth_required
def read_message(user_id: str):
    with sql_client_instance.session_scope() as s:
        s: Session
        current_user = User.find_by_id(s, user_id)
        if current_user is None:
            abort(404, f"{user_id=} not found")
        message = (
            current_user.messages_received.filter(Message.is_read == False)
            .order_by(Message.timestamp)
            .first()
        )
        if message is None:
            return {"status": f"no unread messages for {user_id=}"}
        from_user: User = s.query(User).filter(User.id == message.receiver_id).first()
        message: Message
        message.is_read = 1

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
def get_messages(user_id: str, status: str):
    """
    The task asked for a method to get all the messages , in reality this not to recommend and we should limit
    the amount of messages a single api call can fetch , using pagination and a cursor for following api calls
    """
    try:
        status = MessageFetchRequestStatus(status)
    except ValueError:
        abort(
            400,
            f"Provided {status=} invalid, use {[_status.value for _status in MessageFetchRequestStatus]}",
        )
    with sql_client_instance.session_scope() as s:
        s: Session
        status: MessageFetchRequestStatus
        current_user = User.find_by_id(s, user_id)
        if current_user is None:
            abort(400, f"{user_id=} not found")
        if status.value == MessageFetchRequestStatus.read.value:
            messages = current_user.messages_received.filter(
                Message.is_read == True
            ).all()
        elif status.value == MessageFetchRequestStatus.unread.value:
            messages = current_user.messages_received.filter(
                Message.is_read == False
            ).all()
        elif status.value == MessageFetchRequestStatus.all.value:
            messages = current_user.messages_received.all()
        else:
            raise RuntimeError
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
def delete_message(user_id: str, message_id: str):
    with sql_client_instance.session_scope() as s:
        s: Session
        message = (
            s.query(Message)
            .filter(
                Message.id == message_id,
                or_(Message.receiver_id == user_id, Message.sender_id == user_id),
            )
            .first()
        )
        if message is None:
            return {"status": f"no message found  {message_id=} and {user_id=}"}
        s.delete(message)

    return {"status": "ok"}
