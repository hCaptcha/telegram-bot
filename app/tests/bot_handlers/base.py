import unittest
import time
import datetime
from telegram import Update, Chat, Message, User
from unittest.mock import MagicMock, call

from app.lib.bot import HCaptchaBot
from app.config import get_active_config
from app.extensions import db
from app.models import Channel, Human
from app.tests.test_helpers import BaseCase, AttrDict


class TestBotHandlersBase(BaseCase):
    def setUp(self):
        super().setUp()
        self.hCaptchaBot = HCaptchaBot(get_active_config().TELEGRAM_TOKEN)
        self.bot = self.hCaptchaBot.bot

    def next_id(self):
        return int(time.time() * 1000000)

    def fake_update(self, **params):
        private_chat = Chat(id=1, type="private", first_name="Joe", last_name="Doe")
        user = User(id=1, first_name="Joe", last_name="Doe", is_bot=False)

        chat = params.pop("chat") if params.get("chat", None) else private_chat
        from_user = params.pop("from_user") if params.get("from_user", None) else user

        return Update(
            self.next_id(),
            Message(
                message_id=self.next_id(),
                date=None,
                from_user=from_user,
                chat=chat,
                bot=self.bot,
                **params
            ),
        )


if __name__ == "__main__":
    unittest.main()
