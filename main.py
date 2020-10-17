import logging
import sys

from flask import Flask
from controllers import messages_bp, auth_bp

FORMAT = (
    f"%(levelname).1s: %(asctime)s %(name)s %(threadName)s %(funcName)s : %(message)s"
)

logging.basicConfig(level=logging.INFO, format=FORMAT, stream=sys.stdout)
log = logging.getLogger(__name__)


app = Flask(__name__)
app.register_blueprint(messages_bp, url_prefix="/messages")
app.register_blueprint(auth_bp, url_prefix="/users")


@app.route("/")
def index():
    return "<h1>Welcome to Message app</h1>"


if __name__ == "__main__":
    log.info("starting flask dev server")
    app.run("127.0.0.1", "5000", debug=True, use_reloader=True)
