import os
from dotenv import load_dotenv
from flask import current_app

load_dotenv()


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    HCAPTCHA_SECRET = os.getenv("HCAPTCHA_SECRET", None)
    HCAPTCHA_POST_URI = os.getenv(
        "HCAPTCHA_POST_URI", "https://hcaptcha.com/siteverify"
    )
    HCAPTCHA_SITE_KEY = os.getenv("HCAPTCHA_SITE_KEY", None)
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    MESSAGE_CHARS_LIMIT = os.getenv(
        "MESSAGE_TRIM_CHARS_LIMIT", 30
    )  # used trim some messages sent from the bot
    TELEGRAM_USERNAME = os.getenv("TELEGRAM_USERNAME", None)
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", None)
    APP_URL = os.getenv("APP_URL", None)

    if not TELEGRAM_USERNAME:
        raise ValueError("TELEGRAM_USERNAME is not set")

    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN is not set")

    if not HCAPTCHA_SECRET:
        raise ValueError("HCAPTCHA_SECRET is not set")

    if not HCAPTCHA_SITE_KEY:
        raise ValueError("HCAPTCHA_SITE_KEY is not set")


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEBUG = True


class DevelopmentConfig(Config):
    DEBUG = True
    APP_URL = os.getenv("APP_URL", "http://127.0.0.1:8000/")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://localhost/thb")


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"


app_config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "staging": StagingConfig,
    "production": ProductionConfig,
}


def active_config_name():
    config_name = None

    if current_app:
        config_name = current_app.config_name

    if not config_name:
        config_name = os.getenv("APP_SETTINGS", "development")

    return config_name


def get_active_config():
    return app_config[active_config_name()]


def should_run_webhook():
    return active_config_name() in ["staging", "production"]
