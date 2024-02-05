#!/usr/bin/python

import locale
import os
from typing import Dict, Optional

from flask import Flask, Response, send_from_directory

from ekoli_calendar.actions import main_calendar_action
from ekoli_calendar.app_utils import task_details_for_markup


def create_app(config_overrides: Optional[Dict[str, str]] = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object("config")

    if config_overrides is not None:
        app.config.from_mapping(config_overrides)

    if app.config["LOCALE"] is not None:
        try:
            locale.setlocale(locale.LC_ALL, app.config["LOCALE"])
        except locale.Error as e:
            app.logger.warning("{} ({})".format(str(e), app.config["LOCALE"]))

    # To avoid main_calendar_action below shallowing favicon requests and generating error logs
    @app.route("/favicon.ico")
    def favicon() -> Response:
        return send_from_directory(
            os.path.join(app.root_path, "static"),
            "favicon.ico",
            mimetype="image/vnd.microsoft.icon",
        )

    app.add_url_rule("/", "main_calendar_action", main_calendar_action, methods=["GET"])
    app.jinja_env.filters["task_details_for_markup"] = task_details_for_markup

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=app.config["DEBUG"], host=app.config["HOST_IP"])
