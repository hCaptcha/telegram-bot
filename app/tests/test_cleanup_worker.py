import unittest
from unittest.mock import MagicMock, patch

from telegram.error import BadRequest

from app import create_app
from app.config import app_config
from app.extensions import db
from app.lib.bot import HCaptchaBot
from app.lib.cleanup_worker import CleanupWorker
from app.models import Message
from test_helpers import BaseCase


class TestCleanupWorker(BaseCase):
    def setUp(self):
        super().setUp()
        self.test_bot = HCaptchaBot(app_config["testing"].TELEGRAM_TOKEN).bot
        self.test_app = create_app("testing")
        # hours will leads to delete all messages when running the worker
        self.test_worker = CleanupWorker(self.test_bot, self.test_app, minutes=0)

    def test_run_simpe(self):
        """ Delete a message that just added to db """
        self.test_bot.delete_message = MagicMock(return_value=True)

        # Add a message to the db
        message = Message(user_id="2", chat_id="2", message_id="2")
        db.session.add(message)
        db.session.commit()

        self.test_worker.cleanup()
        self.test_bot.delete_message.assert_called()
        message = Message.query.filter_by(
            user_id="2", chat_id="2", message_id="2"
        ).one_or_none()
        assert message is None

    def test_run_badrequest(self):
        """ Delete a message that is deleted on the telegram api <- BadRequest """
        self.test_bot.delete_message = MagicMock(
            side_effect=BadRequest("Message not found")
        )
        # Add a message to the db
        message = Message(user_id="3", chat_id="3", message_id="3")
        db.session.add(message)
        db.session.commit()

        self.test_worker.cleanup()
        self.test_bot.delete_message.assert_called()
        self.test_bot.delete_message.assert_called_with(chat_id="3", message_id="3")
        message = Message.query.filter_by(
            user_id="3", chat_id="3", message_id="3"
        ).one_or_none()
        assert message is None

    def test_run_telegram_denied(self):
        """Delete a message that won't be deleted on Telegram because of
        Telegram api limitations
        """
        self.test_bot.delete_message = MagicMock(return_value=False)
        # Add a message to the db
        message = Message(user_id="4", chat_id="4", message_id="4")
        db.session.add(message)
        db.session.commit()

        self.test_worker.cleanup()
        message = Message.query.filter_by(
            user_id="4", chat_id="4", message_id="4"
        ).one_or_none()
        assert message is not None


if __name__ == "__main__":
    unittest.main()
