from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import atexit

from app import captcha, webhook
from app.config import app_config, active_config_name, get_active_config
from app.lib.bot import HCaptchaBot


def create_app(config_name=active_config_name()):
    app = Flask(__name__.split(".")[0])
    app.config.from_object(app_config[config_name])
    app.config_name = config_name

    with app.app_context():
        register_extensions(app)
        register_blueprints(app)
        register_bot(app, config_name)

        atexit.register(_handle_exit(app))

        return app


def register_bot(app, config_name):
    app.bot_instance = HCaptchaBot(get_active_config().TELEGRAM_TOKEN, app)

    # Don't explicitly run the bot in testing env
    if config_name != "testing":
        app.bot_instance.setup()
        app.bot_instance.run()


def _handle_exit(app):
    def hanlder():
        app.bot_instance.exit()

    return hanlder


def register_extensions(app):
    db = SQLAlchemy()

    with app.app_context():
        db.init_app(app)


def register_blueprints(app):
    app.register_blueprint(captcha.views.blueprint)
    app.register_blueprint(webhook.views.blueprint)
