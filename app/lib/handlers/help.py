from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from app.lib.handlers.base import BaseHandler


class HelpCommand(BaseHandler):
    def handler(self, update: Update, context: CallbackContext):
        help_message = """
Available commands:

/hi - check your status or verify yourself
/restrict <super_group> - restrict newly joined users in <super_group>. bot should have admin permissions.
/stats - show statistics about humans/bots from the entire pool
"""

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=help_message,
            parse_mode=ParseMode.MARKDOWN,
        )
