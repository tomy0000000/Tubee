"""Main Application of Tubee"""
import json
import logging.config
from os import path

from authlib.integrations.flask_client import OAuth
from celery import Celery
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

from tubee.config import config

__version__ = "dev_20210123"

db = SQLAlchemy()
bcrypt = Bcrypt()
celery = Celery(__name__)
login_manager = LoginManager()
migrate = Migrate()
moment = Moment()
oauth = OAuth()


def create_app(config_name, coverage=None):
    app = Flask(__name__, instance_relative_config=True)
    app.version = __version__
    app.config.from_object(config[config_name])
    external_config = path.join(app.instance_path, "logging.cfg")
    load_external = path.exists(external_config) and path.isfile(external_config)
    if load_external:
        with open(external_config) as json_file:
            logging.config.dictConfig(json.load(json_file))

    db.init_app(app)
    app.db = db
    config[config_name].init_app(app)

    if coverage:
        app.coverage = coverage

    if load_external:
        app.logger.info("External Logging Config Loaded")

    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    moment.init_app(app)
    oauth.init_app(app)
    celery.conf.update(app.config)

    login_manager.login_view = "user.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"
    login_manager.needs_refresh_message = "Please reauthenticate to access this page."
    login_manager.needs_refresh_message_category = "warning"
    oauth.register(
        name="LineNotify",
        access_token_url="https://notify-bot.line.me/oauth/token",
        access_token_params=None,
        authorize_url="https://notify-bot.line.me/oauth/authorize",
        authorize_params=dict(response_type="code", scope="notify"),
        api_base_url="https://notify-api.line.me/",
        client_kwargs=None,
        fetch_token=lambda: dict(
            access_token=current_user._line_notify_credentials, token_type="bearer"
        ),
    )

    from . import commands, routes

    app.shell_context_processor(commands.make_shell_context)
    app.cli.add_command(commands.deploy)
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.docker_cli)

    app.register_blueprint(routes.main_blueprint)
    app.register_blueprint(routes.admin_blueprint, url_prefix="/admin")
    app.register_blueprint(routes.api_blueprint, url_prefix="/api")
    app.register_blueprint(routes.api_action_blueprint, url_prefix="/api/action")
    app.register_blueprint(routes.api_channel_blueprint, url_prefix="/api/channel")
    app.register_blueprint(routes.api_tag_blueprint, url_prefix="/api/tag")
    app.register_blueprint(routes.api_task_blueprint, url_prefix="/api/task")
    app.register_blueprint(routes.user_blueprint, url_prefix="/user")
    if app.debug:
        app.register_blueprint(routes.dev_blueprint, url_prefix="/dev")
    else:
        app.register_blueprint(routes.handler_blueprint)

    return app
