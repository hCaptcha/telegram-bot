import logging
from datetime import datetime

from telegram import ChatPermissions, ParseMode, Update
from telegram.ext import CallbackContext

from app.extensions import db
from app.lib.cleanup_worker import CleanupWorker
from app.models import Human, Message


def app_context(func):
    def func_wrapper(self, *args, **kwargs):
        if self.app:
            with self.app.app_context():
                return func(self, *args, **kwargs)
        else:
            return func(self, *args, **kwargs)

    return func_wrapper


class BaseHandler:
    def __init__(self, app=None):
        self.app = app
        self.logger = logging.getLogger("bot")

    def handler(self, update: Update, context: CallbackContext):
        pass

    def is_verified(self, user_id):
        return db.session.query(
            Human.query.filter(
                Human.user_id == str(user_id), Human.verified == True
            ).exists()
        ).scalar()

    def verify(self, bot, chat_id, user_id, user_name, callback_chat_id):
        """
        - Record that the user is human
        - Incase the chat was in the group (`callback_chat_id` param is set), remove restrictions for `user_id`
        - Notify user about the verification
        """

        if self.is_verified(user_id):
            return

        db.session.add(
            Human(
                user_id=user_id,
                user_name=user_name,
                verified=True,
                verification_date=datetime.today(),
            )
        )
        db.session.commit()

        self.app.bot_instance.worker.cleanup_all_user_messages(chat_id, user_id)

        self.logger.info(
            f"Recording that user is human, chat_id: {chat_id}, user_id: {user_id}, user_name: {user_name}, callback_chat_id: {callback_chat_id} ..."
        )

        # user is here from a group
        if callback_chat_id and callback_chat_id != "None":
            self.logger.info("Removing restctions...")
            self.remove_restrictions(bot, callback_chat_id, user_id, user_name)

            self.logger.info("Sending notification...")
            res = bot.send_message(
                chat_id,
                f"**Thanks {user_name}! You are now allowed to chat.**",
                parse_mode=ParseMode.MARKDOWN,
            )
            self.add_message_info(res["message_id"], res["chat"]["id"])
        else:
            self.logger.info("Private message, sending notification...")
            bot.send_message(
                chat_id,
                f"**Thanks {user_name}! You are now verified.**",
                parse_mode=ParseMode.MARKDOWN,
            )

    def remove_restrictions(self, bot, chat_id, user_id, user_name):
        """
        Remove chat restrictions for user
        """
        self.logger.info(f"User is human. username: {user_name}, id: {user_id}")
        self.logger.info("Removing restctions...")

        bot.restrict_chat_member(
            chat_id,
            user_id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
            ),
        )

    def can_restrict_channel(self, bot, chat_id):
        chat_type = bot.get_chat(chat_id).type
        bot_status = bot.get_chat_member(chat_id, bot.id).status
        self.logger.info(
            f"chat_id: {chat_id} | chat_type: {chat_type} | bot_status: {bot_status}"
        )
        return chat_type == "supergroup" and bot_status == "administrator"

    def add_message_info(self, message_id, chat_id, user_id):
        """ Add a message(chat_id, message_id) to the db, so we can delete the message later """
        db.session.add(
            Message(
                chat_id=chat_id,
                message_id=message_id,
                user_id=str(user_id),
            )
        )
        db.session.commit()
        self.logger.debug(f"Recording the message that just sent ...")
