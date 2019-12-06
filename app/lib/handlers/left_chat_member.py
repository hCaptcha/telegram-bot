from telegram import Update
from telegram.ext import CallbackContext

from app.extensions import db
from app.models import Channel
from app.lib.handlers.base import BaseHandler, app_context


class LeftChatMemberFilter(BaseHandler):
    @app_context
    def handler(self, update: Update, context: CallbackContext):
        message = update.message

        # Only handle case when bot was removed from channel
        if not message.left_chat_member.id == context.bot.id:
            return

        channel = Channel.query.filter(
            Channel.chat_id == str(message.chat_id)
        ).one_or_none()

        if not channel:
            self.logger.warning(
                f"Supposed to get removed from channel that doesn't exists, chat_id: {message.chat_id}"
            )
            return

        self.logger.info(f"Leaving chat_id: {message.chat_id}...")

        db.session.delete(channel)
        db.session.commit()
