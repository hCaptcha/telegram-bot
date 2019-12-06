import unittest
from unittest.mock import MagicMock, call

from base import TestBotHandlersBase
from app.lib.handlers.base import BaseHandler
from app.extensions import db
from app.models import Human
from app.tests.test_helpers import AttrDict


class TestHandler(TestBotHandlersBase):
    def setUp(self):
        super().setUp()
        self.command = BaseHandler(self.app)

    def test_is_verified(self):
        h = Human.query.filter_by(user_id="1", user_name="joe").one_or_none()

        h.verified = True
        db.session.commit()

        self.assertTrue(self.command.is_verified(h.user_id))

        h.verified = False
        db.session.commit()

        self.assertFalse(self.command.is_verified(h.user_id))

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
