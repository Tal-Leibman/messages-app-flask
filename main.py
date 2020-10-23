import logging
import sys

import click
from flask import Flask

from controllers import messages_bp, auth_bp
from models import db


@click.command()
@click.option("--debug", default=False,type=click.BOOL)
@click.option("--port", type=int, envvar="PORT", help="Port to listen for requests")
@click.option(
    "--db-url", envvar="DATABASE_URL", help="full sql data base connection url"
)
@click.option("--log-level", default="INFO")
@click.option(
    "--log-format",
    default="%(levelname).1s: %(asctime)s %(name)s %(threadName)s %(funcName)s : %(message)s",
)
@click.option("--max-messages-fetch", type=click.IntRange(1, 100), default=5)
def main(debug, port, db_url, log_level, log_format, max_messages_fetch):
    logging.basicConfig(
        level=logging.getLevelName(log_level), format=log_format, stream=sys.stdout
    )
    log = logging.getLogger(__name__)
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAX_MESSAGES_FETCH_COUNT"] = max_messages_fetch
    db.app = app
    db.init_app(app)
    db.create_all()
    app.register_blueprint(messages_bp, url_prefix="/messages")
    app.register_blueprint(auth_bp, url_prefix="/auth")

    if debug:
        log.info("starting flask dev server")
        app.run("127.0.0.1", port, debug=True, use_reloader=True)
    else:
        import waitress

        log.info(f"starting prod server {port=}")
        waitress.serve(app, port=port)


if __name__ == "__main__":
    main()
