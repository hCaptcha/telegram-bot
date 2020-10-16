from telegram import Update
from telegram.ext import CallbackContext

from app.extensions import db
from app.lib.handlers.base import BaseHandler, app_context
from app.models import Channel


class ChatCreatedFilter(BaseHandler):
    @app_context
    def handler(self, update: Update, context: CallbackContext):
        """
        When added to a group (either at creation or later):
        - Send welcome message.
        - Add channel to the database.
        """
        message = update.message

        self.logger.info(f"Bot was invited. sending welcome message...")

        text = f"Hi, {message.from_user.username} invited me here to keep <{message.chat.title}> human! If you'd like to participate, just message me 'hi' to start. I'll remember you're human if we've spoken before :)"

        db.session.add(Channel(chat_id=message.chat_id, name=message.chat.title))
        db.session.commit()

        context.bot.send_message(chat_id=message.chat_id, text=text)
