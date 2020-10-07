import unittest
from unittest.mock import MagicMock, patch
from telegram.error import BadRequest
from app.lib.bot import HCaptchaBot
from app.lib.cleanup_worker import CleanupWorker
from app.lib.utils import cleanup_message
from app.config import app_config
from app.extensions import db
from test_helpers import BaseCase
from app import create_app
from app.models import Message


def _run(self):
    self._cleanup()

def _bot_delete_message_badrequest(*args, **kwargs):
    raise BadRequest("Message not found")    

def _bot_delete_message_denied(*args, **kwargs):
    return False

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

        self.test_worker._cleanup()
        self.test_bot.delete_message.assert_called()
        m = Message.query.filter_by(user_id="2", chat_id="2", message_id="2").one_or_none()
        assert m is None

    def test_run_badrequest(self):
        """ Delete a message that is deleted on the telegram api <- BadRequest """
        # Add a message to the db
        message = Message(user_id="3", chat_id="3", message_id="3")
        db.session.add(message)
        db.session.commit()

        with patch.object(self.test_bot, "delete_message", _bot_delete_message_badrequest):
            self.test_worker._cleanup()
            self.test_bot.delete_message.assert_called()
            self.test_bot.delete_message.assert_called_with(user_id="3", chat_id="3", message_id="3")
            m = Message.query.filter_by(user_id="3", chat_id="3", message_id="3").one_or_none()
            assert m is None

    def test_run_badrequest(self):
        """ Delete a message that won't be delted on the telegram because of it's api limitations """
        # Add a message to the db
        message = Message(user_id="4", chat_id="4", message_id="4")
        db.session.add(message)
        db.session.commit()

        with patch.object(self.test_bot, "delete_message", _bot_delete_message_denied):
            self.test_worker._cleanup()
            m = Message.query.filter_by(user_id="4", chat_id="4", message_id="4").one_or_none()
            assert m is not None
        db.session.commit()

if __name__ == "__main__":
    unittest.main()
