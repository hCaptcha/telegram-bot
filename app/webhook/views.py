from flask import Blueprint, current_app, request
from telegram import Update

from app.config import get_active_config

blueprint = Blueprint("webhook", __name__)


@blueprint.route("/" + get_active_config().TELEGRAM_TOKEN, methods=["POST"])
def webhook():
    update = request.get_json()

    current_app.bot_instance.update_queue.put(
        Update.de_json(update, current_app.bot_instance.bot)
    )

    return ("", 204)
