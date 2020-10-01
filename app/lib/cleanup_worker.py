import schedule
import logging
from datetime import datetime, timedelta
from telegram.error import BadRequest
from time import sleep
from app.extensions import db

from app.models import Message
from app.lib.handlers.base import app_context


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)

logger = logging.getLogger("cleanup_worker")


class CleanupWorker:
    def __init__(self, bot, app=None, hours=45):
        self.bot = bot
        self.hours = hours
        self.app = app
        schedule.every(self.hours).hours.do(self._cleanup)

    def run(self):
        while True:
            schedule.run_pending()
            sleep(1)

    @app_context
    def _cleanup(self):
        messages = db.session.query(Message).filter(
                   Message.created_date<=(datetime.utcnow()-timedelta(hours=self.hours))
        ).all()
        logger.info(
                f"Start to cleaning up {len(messages)} message..."
        )
        
        deleted = 0
        for m in messages:
            must_delete = False
            try:
                must_delete = self.bot.delete_message(chat_id=m.chat_id, message_id=m.message_id)
            # Skip if the message not found for any reason
            except BadRequest as e:
                logger.debug(
                        f"While deleting a bot message: {e}"
                )
                must_delete = True
            except Exception as e:
                logger.debug(
                        f"While deleting a bot message, chat_id={m.chat_id} , message_id={m.message_id}: {e}"
                )
                continue
            if must_delete:
                db.session.delete(m)
                db.session.commit()
                deleted += 1

        logger.info(
                f"Cleaning up {deleted} message done."
        )
