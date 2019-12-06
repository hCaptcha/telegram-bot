from telegram import Update
from telegram.ext import CallbackContext

from app.lib.handlers.base import BaseHandler, app_context
from app.config import get_active_config
from app.lib.handlers.help import HelpCommand


class UnknownCommand(BaseHandler):
    @app_context
    def handler(self, update: Update, context: CallbackContext):
        command = update.message.text[: get_active_config().MESSAGE_CHARS_LIMIT] + (
            update.message.text[get_active_config().MESSAGE_CHARS_LIMIT :] and "..."
        )

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=f"Sorry, didn't recognize this command:\n{command}",
        )
        HelpCommand(self.app).handler(update, context)
