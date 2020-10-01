import json
from telegram import Update, ParseMode, ChatPermissions
from telegram.ext import CallbackContext

from app.extensions import db
from app.lib.handlers.base import BaseHandler, app_context
from app.lib.handlers.chat_created import ChatCreatedFilter
from app.config import get_active_config
from app.models import Channel


class NewChatMembersFilter(BaseHandler):
    @app_context
    def handler(self, update: Update, context: CallbackContext):
        """
        Iterate over newly joined chat users and for each user: restrict them and send the hcaptcha link
        """
        message = update.message
        chat_id = message.chat_id

        for user in message.new_chat_members:
            self.logger.info(
                f"New user joined. chat_id: {chat_id}, id: {user.id}, username: {user.username}"
            )

            # Send welcome message
            if user.id == context.bot.id:
                ChatCreatedFilter(self.app).handler(update, context)
                return

            if not self.can_restrict_channel(context.bot, chat_id):
                self.logger.info(f"we can't restrict this chat: {chat_id}")
                break

            if not self.should_restrict_channel(chat_id):
                self.logger.info(f"we shouldn't restrict this chat: {chat_id}")
                break

            if self.is_verified(user.id):
                self.logger.info(f"user: {user.id} is already verified")
                break

            self.logger.info("Restricting...")
            context.bot.restrict_chat_member(
                message.chat_id,
                user.id,
                permissions=ChatPermissions(
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_other_messages=False,
                ),
            )

            self.logger.info("Sending bot link...")
            res = self.send_bot_link(context.bot, chat_id, user)
            self.add_message_info(res['message_id'], res['chat']['id'])

    def send_bot_link(self, bot, chat_id, user):
        return bot.send_message(
            chat_id,
            f"Hi {user.name} 👋! Please click the following link to verify yourself before you're allowed to chat.**",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {
                                "text": "Initiate verification",
                                "url": self.get_bot_link(chat_id),
                            }
                        ]
                    ]
                }
            ),
        )

    def get_bot_link(self, chat_id):
        link = f"https://t.me/{get_active_config().TELEGRAM_USERNAME}?start={chat_id}"
        self.logger.info(f"bot link: {link}")

        return link

    def should_restrict_channel(self, chat_id):
        return db.session.query(
            Channel.query.filter(
                Channel.chat_id == str(chat_id), Channel.restrict == True
            ).exists()
        ).scalar()
