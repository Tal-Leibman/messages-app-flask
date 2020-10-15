import logging

from flask import Blueprint, request, abort
from db import mysql_client_instance

log = logging.getLogger(__name__)
users_bp = Blueprint("users", __name__)
