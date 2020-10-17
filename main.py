import logging
import os
import sys

from flask import Flask

from controllers import messages_bp, auth_bp
from models import db

FORMAT = (
    f"%(levelname).1s: %(asctime)s %(name)s %(threadName)s %(funcName)s : %(message)s"
)
logging.basicConfig(level=logging.INFO, format=FORMAT, stream=sys.stdout)
log = logging.getLogger(__name__)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.app = app
db.init_app(app)
db.create_all()
app.register_blueprint(messages_bp, url_prefix="/messages")
app.register_blueprint(auth_bp, url_prefix="/users")


if __name__ == "__main__":
    log.info("starting flask dev server")
    app.run("127.0.0.1", "5000", debug=True, use_reloader=True)
