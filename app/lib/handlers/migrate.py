from telegram import Update
from telegram.ext import CallbackContext

from app.extensions import db
from app.lib.handlers.base import BaseHandler, app_context
from app.models import Channel


class MigrateFilter(BaseHandler):
    @app_context
    def handler(self, update: Update, context: CallbackContext):
        message = update.message

        # Incase we get migrate_to_chat_id update, ignore. We'll be getting another update
        # from migrate_from_chat_id after it.
        if not message.migrate_from_chat_id:
            return

        original_chat_id = str(message.migrate_from_chat_id)
        new_chat_id = str(message.chat_id)

        self.logger.debug(f"migrating chat_id from {original_chat_id} to {new_chat_id}")

        channel = Channel.query.filter(
            Channel.chat_id == original_chat_id
        ).one_or_none()

        if not channel:
            self.logger.error(
                f"Unable to find a channel that should exists: original_chat_id: {original_chat_id}, new_chat_id: {new_chat_id}"
            )
            return

        channel.chat_id = new_chat_id
        db.session.commit()
