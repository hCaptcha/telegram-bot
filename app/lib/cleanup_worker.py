import schedule
import logging
from datetime import datetime, timedelta
from telegram.error import BadRequest
from time import sleep
from app.extensions import db

from app.models import Message
from app.lib.handlers.base import app_context
from app.config import get_active_config
from app.lib.utils import cleanup_message


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)

logger = logging.getLogger("cleanup_worker")

class CleanupWorker:
    def __init__(self, bot, app=None, minutes=None):
        self.bot = bot
        self.app = app

        self.minutes = minutes or int(get_active_config().CLEANUP_PERIOD_MINUTES)
        schedule.every(self.minutes).minutes.do(self._cleanup)

    def run(self):
        while True:
            schedule.run_pending()
            sleep(1)

    @app_context
    def _cleanup(self):
        # If no folowup of captcha completion, then we can just cleanup all of messages that are older than self.minutes ago.
        messages = db.session.query(Message).filter(
                   Message.created_date<=(datetime.now()-timedelta(minutes=0))
        ).all()
        logger.info(
                f"Start to cleaning up {len(messages)} message..."
        )
        
        deleted = 0
        for m in messages:
            deleted += cleanup_message(self.bot, m.id, m.chat_id, m.message_id)

        logger.info(
                f"Cleaning up {deleted} message done."
        )
