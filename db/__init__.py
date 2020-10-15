import os

from .mysql_client import MySqlClient, SqlTableDeclarativeBase
from .models import Message, User,MessageResponse

mysql_client_instance = MySqlClient.get_mysql_client(
    host=os.environ["MYSQL_HOST"],
    user=os.environ["MYSQL_USER"],
    password=os.environ["MYSQL_PASSWORD"],
    scheme="messages_app",
)
