from telegram import Update
from telegram.ext import CallbackContext

from app.extensions import db
from app.models import Channel, Human, HumanChannelMember, Bot, BotChannelMember
from app.lib.handlers.base import BaseHandler, app_context


class LeftChatMemberFilter(BaseHandler):
    @app_context
    def handler(self, update: Update, context: CallbackContext):
        message = update.message

        # Only handle case when bot was removed from channel
        if not message.left_chat_member.id == context.bot.id:
            if message.left_chat_member.is_bot:
                db.session.query(BotChannelMember).join(Bot).join(Channel).filter(
                    Bot.user_id == message.left_chat_member.id,
                    Channel.chat_id == message.chat_id
                ).delete()
                db.session.commit()
            else:
                db.session.query(HumanChannelMember).join(Human).join(Channel).filter(
                    Human.user_id == message.left_chat_member.id,
                    Channel.chat_id == message.chat_id
                ).delete()
                db.session.commit()

        
        channel = Channel.query.filter(
            Channel.chat_id == str(message.chat_id)
        ).one_or_none()

        if not channel:
            self.logger.warning(
                f"Supposed to get removed from channel that doesn't exists, chat_id: {message.chat_id}"
            )
            return

        self.logger.info(f"Leaving chat_id: {message.chat_id}...")
        
        # Delete 
        session = db.session.begin()
        try:
            # Is this a desired behaviour?
            session.query(BotChannelMemeber).join(Bot).join(Channel).filter(
                Channel.chat_id == message.chat_id
            ).delete()
            session.flush()
            session.query(HumanChannelMember).join(Human).join(Channel).filter(
                Channel.chat_id == message.chat_id
            ).delete()
            session.flush()
            session.delete(channel)
            session.commit()
        except:
            session.rollback()
