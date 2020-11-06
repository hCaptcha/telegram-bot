from telegram import Update
from telegram.ext import CallbackContext

from app.extensions import db
from app.lib.handlers.base import BaseHandler, app_context
from app.models import Channel


class RestrcitCommand(BaseHandler):
    @app_context
    def handler(self, update: Update, context: CallbackContext):
        try:
            if not context.args:
                raise ValueError("args is required")

            channel_name = " ".join(context.args)
            channel = Channel.query.filter(Channel.name == channel_name).one_or_none()
            if channel is None:
                update.message.reply_text(
                    f"{channel_name} is not registered to the bot, please invite me there first."
                )
                return None

            # Only group admins are allowed to restrict a channel
            if not self.is_admin_on_channel(
                context.bot, channel.chat_id, update.message.from_user.id
            ):
                update.message.reply_text(
                    f"You must be an admin on <{channel_name}> to restrict it."
                )
                return

            if channel.restrict:
                update.message.reply_text(f"<{channel_name}> is already restricted.")
                return

            if self.can_restrict_channel(context.bot, channel.chat_id):
                channel.restrict = True
                db.session.commit()
                update.message.reply_text(
                    f"New users joining <{channel_name}> will be asked to verify themselves before being able to send new messages"
                )
            else:
                update.message.reply_text(
                    f"{channel_name} must be a supergroup and the bot must be have admin permissions"
                )

        except (IndexError, ValueError, Exception):
            update.message.reply_text("Usage: /restrict <channel>")

    def is_admin_on_channel(self, bot, chat_id, user_id):
        chat = bot.get_chat(chat_id)
        return any(
            filter(
                lambda administrator: administrator.user.id == user_id,
                chat.get_administrators(),
            )
        )
