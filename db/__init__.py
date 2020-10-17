import os

from .client import SqlClient, SqlTableDeclarativeBase
from .models import (
    Message,
    User,
    MessageResponse,
    ParseWriteMessageRequest,
    MessageFetchRequestStatus,
)

sql_client_instance = SqlClient(os.environ["DATABASE_URL"])
sql_client_instance.create_all_tables()
