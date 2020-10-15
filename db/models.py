import dataclasses

from dataclasses_json import DataClassJsonMixin
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey

from .mysql_client import SqlTableDeclarativeBase


class User(SqlTableDeclarativeBase):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(50), unique=True, nullable=False)


class Message(SqlTableDeclarativeBase):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    body = Column(String(1000), unique=True, nullable=False)
    subject = Column(String(160), unique=True, nullable=False)
    timestamp = Column(Integer, nullable=False)
    is_read = Column(Boolean, nullable=False)


@dataclasses.dataclass(frozen=True)
class MessageResponse(DataClassJsonMixin):
    sent_from: str
    subject: str
    body: str
    timestamp: int
