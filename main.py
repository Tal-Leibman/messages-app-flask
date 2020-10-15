import logging
import os
import sys

from flask import Flask
from waitress import serve

from controllers import messages_bp, users_bp


FORMAT = (
    f"%(levelname).1s: %(asctime)s %(name)s %(threadName)s %(funcName)s : %(message)s"
)

logging.basicConfig(level=logging.INFO, format=FORMAT, stream=sys.stdout)
log = logging.getLogger(__name__)
IS_DEBUG = os.getenv("IS_DEBUG_ENVIRONMENT", "1") == "1"

if IS_DEBUG:
    from dotenv import load_dotenv

    log.info("Running in debug mode loading .env file")
    load_dotenv(".env")

app = Flask(__name__)
app.register_blueprint(messages_bp, url_prefix="messages")
app.register_blueprint(users_bp, url_prefix="users")


if __name__ == "__main__":
    if IS_DEBUG:
        log.info("starting flask dev server")
        app.run("127.0.0.1", "5000", debug=True, use_reloader=True)
    else:
        log.info("starting waitress server")
        serve(app)
