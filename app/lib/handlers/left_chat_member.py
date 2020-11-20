from telegram import Update
from telegram.ext import CallbackContext

from app.extensions import db
from app.lib.handlers.base import BaseHandler, app_context, catch_error
from app.models import (
    Bot,
    BotChannelMember,
    Channel,
    Human,
    HumanChannelMember,
)


class LeftChatMemberFilter(BaseHandler):
    @app_context
    @catch_error
    def handler(self, update: Update, context: CallbackContext):
        message = update.message

        channel = Channel.query.filter(
            Channel.chat_id == str(message.chat_id)
        ).one_or_none()

        if not channel:
            self.logger.warning(
                f"Supposed to get removed from channel that doesn't exists, chat_id: {message.chat_id}"
            )
            return

        # Only handle case when bot was removed from channel
        if not message.left_chat_member.id == context.bot.id:
            if message.left_chat_member.is_bot:
                bot = (
                    db.session.query(Bot)
                    .filter_by(user_id=str(message.left_chat_member.id))
                    .one_or_none()
                )
                if bot is None:
                    # Should never be called
                    return
                db.session.query(BotChannelMember).filter(
                    BotChannelMember.bot_id == bot.id,
                    BotChannelMember.channel_id == channel.id,
                ).delete()
                db.session.commit()
            else:
                human = (
                    db.session.query(Human)
                    .filter_by(user_id=str(message.left_chat_member.id))
                    .one_or_none()
                )
                if human is None:
                    # Should never be called
                    return
                db.session.query(HumanChannelMember).filter(
                    HumanChannelMember.human_id == human.id,
                    HumanChannelMember.channel_id == channel.id,
                ).delete()
                db.session.commit()
            return

        self.logger.info(f"Leaving chat_id: {message.chat_id}...")

        # Delete
        # Is this a desired behaviour?
        db.session.query(BotChannelMember).filter(
            BotChannelMember.channel_id == channel.id
        ).delete()
        db.session.flush()
        db.session.query(HumanChannelMember).filter(
            HumanChannelMember.channel_id == channel.id
        ).delete()
        db.session.flush()
        db.session.delete(channel)
        db.session.commit()
