import dataclasses
from datetime import datetime
from enum import Enum
from typing import Optional

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


class Message(db.Model):
    __tablename__ = "message"
    id = Column(Integer, primary_key=True, autoincrement=True)

    sender_id = Column(Integer, ForeignKey("user.id"))
    receiver_id = Column(Integer, ForeignKey("user.id"))

    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])

    body = Column(String(1000), nullable=False)
    subject = Column(String(160), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    is_read = Column(Boolean, nullable=False, default=0)


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

    @property
    def messages_received(self) -> Query:
        return self.query(Message).filter(Message.receiver_id == self.id)

    @property
    def messages_sent(self) -> Query:
        return self.query(Message).filter(Message.sender_id == self.id)

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


class MessageFetchRequestStatus(Enum):
    read = "read"
    unread = "unread"
    all = "all"
