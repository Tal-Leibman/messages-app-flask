import dataclasses
from datetime import datetime
from enum import Enum
from typing import Optional, Literal
import bcrypt
from dataclasses_json import DataClassJsonMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    LargeBinary,
)
from sqlalchemy.orm import relationship, Query
from werkzeug.security import safe_str_cmp

db = SQLAlchemy()


class MessageFetchRequestStatus(Enum):
    all_read = "all_read"
    all_unread = "all_unread"
    all = "all"


class MessagesUsers(db.Model):
    __tablename__ = "messages_users"

    message_id = Column(Integer, ForeignKey("message.id"), primary_key=True)
    message = relationship("Message", foreign_keys=[message_id])

    viewer_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    viewer = relationship("User", foreign_keys=[viewer_id])

    sender_id = Column(Integer, ForeignKey("user.id"))
    receiver_id = Column(Integer, ForeignKey("user.id"))
    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
    is_read = Column(Boolean, nullable=False, default=False)

    @classmethod
    def get_by_viewer_id(
        cls, viewer_id: str, message_id
    ) -> Optional["MessagesUsers"]:
        return cls.query.filter(
            MessagesUsers.viewer_id == viewer_id, MessagesUsers.message_id == message_id
        ).first()


class Message(db.Model):
    __tablename__ = "message"
    id = Column(Integer, primary_key=True, autoincrement=True)
    body = Column(String(1000), nullable=False)
    subject = Column(String(160), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)


class User(db.Model):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(50), unique=True, nullable=False)
    password_hash = Column(LargeBinary(128), unique=True, nullable=False)
    password_salt = Column(LargeBinary(128), unique=True, nullable=False)
    auth_token = Column(String(50), unique=True, nullable=True)

    @property
    def password(self):
        raise AttributeError("password not readable")

    @password.setter
    def password(self, password: str):
        salt = bcrypt.gensalt()
        password_bytes = bytes(password, "utf-8")
        self.password_salt = salt
        self.password_hash = bcrypt.hashpw(password_bytes, salt)

    def validate_password(self, password: str) -> bool:
        password_bytes = bytes(password, "utf-8")
        password_hash = bcrypt.hashpw(password_bytes, self.password_salt)
        is_valid = safe_str_cmp(password_hash, self.password_hash)
        return is_valid

    def messages(
        self,
        status: MessageFetchRequestStatus,
        inbox_outbox: Literal["inbox", "outbox"],
    ) -> Query:
        query: Query = MessagesUsers.query.join(MessagesUsers.message).filter(
            MessagesUsers.viewer_id == self.id
        )
        if inbox_outbox == "inbox":
            query = query.filter(MessagesUsers.receiver_id == self.id)
        elif inbox_outbox == "outbox":
            query = query.filter(MessagesUsers.sender_id == self.id)
        else:
            raise ValueError(f"Wrong value for {inbox_outbox=}")
        if status == MessageFetchRequestStatus.all_read:
            query = query.filter(MessagesUsers.is_read == True)
        elif status == MessageFetchRequestStatus.all_unread:
            query = query.filter(MessagesUsers.is_read == False)
        return query

    @classmethod
    def get_by_id(cls, user_id: str) -> Optional["User"]:
        return cls.query.filter(User.id == user_id).first()

    @classmethod
    def get_by_email(cls, email: str) -> Optional["User"]:
        return cls.query.filter(User.email == email).first()

    @classmethod
    def get_by_token(cls, auth_token: str) -> Optional["User"]:
        return cls.query.filter(auth_token == User.auth_token).first()


@dataclasses.dataclass(frozen=True)
class MessageResponse(DataClassJsonMixin):
    message_id: str
    sent_from: str
    subject: str
    body: str
    timestamp: str


@dataclasses.dataclass()
class ParseWriteMessageRequest:
    receiver_id: str
    body: str
    subject: str

    def __post_init__(self):
        if type(self.receiver_id) is int:
            self.receiver_id = str(self.receiver_id)
        elif type(self.receiver_id) is str:
            self.receiver_id = self.receiver_id.strip()
        else:
            raise TypeError(
                f"wrong type receiver_id must be either int or str : {type(self.receiver_id)}"
            )
        if not self.receiver_id:
            raise ValueError("no receiver_id in request")
        self.body = self.body.strip()
        self.subject = self.subject.strip()
        if not self.body and not self.subject:
            raise ValueError("no body or subject found in request")
