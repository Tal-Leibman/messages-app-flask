import dataclasses
from datetime import datetime
from enum import Enum
from typing import Optional
from dataclasses_json import DataClassJsonMixin
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, object_session, Session, Query

from .client import SqlTableDeclarativeBase


class Message(SqlTableDeclarativeBase):
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


class User(SqlTableDeclarativeBase):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(50), unique=True, nullable=False)

    @property
    def messages_received(self) -> Query:
        return (
            object_session(self).query(Message).filter(Message.receiver_id == self.id)
        )

    @property
    def messages_sent(self) -> Query:
        return object_session(self).query(Message).filter(Message.sender_id == self.id)

    @classmethod
    def find_by_id(cls, session: Session, user_id: str) -> Optional["User"]:
        return session.query(User).filter(User.id == user_id).first()


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
        self.receiver_id = self.receiver_id.strip()
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
