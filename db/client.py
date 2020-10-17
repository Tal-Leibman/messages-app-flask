import logging
import os
from contextlib import contextmanager
from threading import Lock
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine.base import Engine
import signal

ECHO_SQL_LOGS = os.getenv("ECHO_SQL_LOGS") == "1"
SqlTableDeclarativeBase = declarative_base()
log = logging.getLogger(__name__)


class SqlClient:
    def __init__(self, connection_string: str):
        self.__engine: Engine = create_engine(
            connection_string,
            echo=ECHO_SQL_LOGS,
            pool_size=20,
            pool_recycle=1200,
            pool_timeout=3600,
        )
        self.__session_maker = sessionmaker(bind=self.__engine)
        signal.signal(signal.SIGTERM, self.__shut_down_client)
        signal.signal(signal.SIGINT, self.__shut_down_client)

    def __shut_down_client(self, _signal, frame):
        log.info(f"{_signal=} received shutting down mysql client")
        self.__engine.dispose()
        exit(0)

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
