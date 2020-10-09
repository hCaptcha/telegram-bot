import logging
from datetime import datetime, timedelta
from time import sleep

import schedule
from telegram.error import BadRequest

from app.config import get_active_config
from app.extensions import db
from app.models import Message

logger = logging.getLogger("cleanup_worker")

class CleanupWorker:
    """ A Worker to periodically delete unused channel messages """
    def __init__(self, bot, app=None, minutes=None):
        self.bot = bot
        self.app = app

        self.minutes = minutes if minutes is not None else\
                int(get_active_config().CLEANUP_PERIOD_MINUTES)
        schedule.every(self.minutes).minutes.do(self.cleanup)

    def run(self):
        """ A cronjob like approach to cleanup messages every self.minutes """
        while True:
            schedule.run_pending()
            sleep(1)

    def cleanup(self):
        """ If no folowup of captcha completion,
        then we can just cleanup all of messages that are older than self.minutes ago.
        """
        with self.app.app_context():
            messages = db.session.query(Message).filter(
                       Message.created_date<=(datetime.now()-timedelta(minutes=self.minutes))
            ).all()
            logger.info(
                    f"Start to cleaning up {len(messages)} message..."
            )
            deleted = 0
            for message in messages:
                deleted += self._cleanup_message(message.id, message.chat_id, message.message_id)

            logger.info(
                    f"Cleaning up {deleted} message done."
            )

    def _cleanup_message(self, _id, chat_id, message_id):
        """ Cleanup a single message from the Telegram api and the db """
        with self.app.app_context():
            must_delete = False
            try:
                must_delete = self.bot.delete_message(chat_id=chat_id, message_id=message_id)
            # Skip if the message not found for any reason
            except BadRequest as e:
                logger.debug(
                        f"While deleting a bot message: {e}"
                )
                must_delete = True
            except Exception as e:
                logger.debug(
                        f"While deleting a bot message, \
                                chat_id={chat_id} , message_id={message_id}: {e}"
                )
                return 0
            if must_delete:
                db.session.query(Message).filter_by(id=_id).delete()
                db.session.commit()
                return 1
            return 0

    def cleanup_all_user_messages(self, chat_id, user_id):
        """ Cleanup all of the user messages from the Telegram api and the db """
        with self.app.app_context():
            messages = db.session.query(Message).filter(
                    Message.user_id==user_id,
                    Message.chat_id==chat_id
            ).all()
            logger.info(
                    f"Start to cleaning up {len(messages)}\
                            message for user_id({user_id})..."
            )
            deleted = 0
            for message in messages:
                deleted += self._cleanup_message(message.id, message.chat_id, message.message_id)
            logger.info(
                    f"Cleaning up {deleted} message done for user_id({user_id})."
            )
