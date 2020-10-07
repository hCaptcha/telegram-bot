import unittest
from unittest.mock import MagicMock, call, patch

from app.lib.bot import HCaptchaBot
from base import TestBotHandlersBase
from app.lib.handlers.base import BaseHandler
from app.extensions import db
from app.models import Human
from app.tests.test_helpers import AttrDict
from app.config import app_config


class TestHandler(TestBotHandlersBase):
    def setUp(self):
        super().setUp()
        self.command = BaseHandler(self.app)
        self.test_bot = HCaptchaBot(app_config["testing"].TELEGRAM_TOKEN).bot

    def test_is_verified(self):
        h = Human.query.filter_by(user_id="1", user_name="joe").one_or_none()

        h.verified = True
        db.session.commit()

        self.assertTrue(self.command.is_verified(h.user_id))

        h.verified = False
        db.session.commit()

        self.assertFalse(self.command.is_verified(h.user_id))

    def test_verify(self):
        self.test_bot.send_message = MagicMock(return_value={"message_id":"1234","chat":{"id":"1234"}})
        with patch('app.lib.handlers.base.cleanup_all_user_messages') as mock_func:
            self.command.verify(self.test_bot, chat_id="1234", user_id="2", user_name="test", callback_chat_id=None) 
            mock_func.assert_called_with(self.test_bot, "1234", "2")



    def test_can_restrict_channel(self):
        self.bot.get_chat = MagicMock(return_value=AttrDict({"type": "group"}))
        self.bot.get_chat_member = MagicMock(
            return_value=AttrDict({"status": "administrator"})
        )

        self.assertFalse(self.command.can_restrict_channel(self.bot, "1"))

        self.bot.get_chat = MagicMock(return_value=AttrDict({"type": "supergroup"}))
        self.bot.get_chat_member = MagicMock(
            return_value=AttrDict({"status": "member"})
        )

        self.assertFalse(self.command.can_restrict_channel(self.bot, "1"))

        self.bot.get_chat = MagicMock(return_value=AttrDict({"type": "supergroup"}))
        self.bot.get_chat_member = MagicMock(
            return_value=AttrDict({"status": "administrator"})
        )

        self.assertTrue(self.command.can_restrict_channel(self.bot, "1"))


if __name__ == "__main__":
    unittest.main()
