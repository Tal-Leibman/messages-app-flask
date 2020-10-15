import logging
import os
from contextlib import contextmanager
from threading import Lock
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

ECHO_SQL_LOGS = os.getenv("ECHO_SQL_LOGS") == "1"
SqlTableDeclarativeBase = declarative_base()
log = logging.getLogger(__name__)


class MySqlClient:
    __CLIENT_TO_CONNECTION_STRING: dict = dict()
    __LOCK = Lock()
    __INSTANCE: Optional["MySqlClient"] = None

    def __init__(self, connection_string: str):
        self.__engine = create_engine(
            connection_string,
            echo=ECHO_SQL_LOGS,
            pool_size=20,
            pool_recycle=1200,
            pool_timeout=3600,
        )
        self.__session_maker = sessionmaker(bind=self.__engine)

    def create_all_tables(self):
        try:
            SqlTableDeclarativeBase.metadata.create_all(self.__engine)
        except Exception as e:
            log.exception(e)

    @contextmanager
    def session_scope(self):
        session = self.__session_maker()
        session: Session
        try:
            yield session
            session.commit()
        except Exception as error:
            log.exception(error)
            session.rollback()
            raise error
        finally:
            session.close()

    @classmethod
    def get_mysql_client(
        cls, user: str, host: str, scheme: str, password: str, port="3306"
    ) -> "MySqlClient":
        """
        returns a single client foreach unique connection string
        """
        connection_string = (
            f"mysql+pymysql://{user}:{password}@{host}:{port}/{scheme}?charset=utf8mb4"
        )
        with cls.__LOCK:
            if connection_string not in cls.__CLIENT_TO_CONNECTION_STRING:
                log.info(f"first connection to mysql at {host=}")
                cls.__CLIENT_TO_CONNECTION_STRING[connection_string] = cls(
                    connection_string
                )
            return cls.__CLIENT_TO_CONNECTION_STRING[connection_string]
