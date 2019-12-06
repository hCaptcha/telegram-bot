import unittest
from telegram import Chat, User
from unittest.mock import MagicMock

from base import TestBotHandlersBase
from app.models import Channel
from app.extensions import db
from app.lib.handlers.left_chat_member import LeftChatMemberFilter


class TestHandler(TestBotHandlersBase):
    def test(self):
        command = LeftChatMemberFilter()
        chat = Chat(id=1, type="supergroup", title="channel 1")
        not_added_chat = Chat(id=2, type="supergroup", title="channel 2")

        random_user = User(id=1, first_name="tt", user_name="test", is_bot=False)
        bot_user = self.bot
        channel = Channel.query.filter_by(chat_id="1").first()

        self.bot.get_updates = MagicMock(
            return_value=[
                # handle case when the bot leave
                self.fake_update(left_chat_member=bot_user, chat=chat),
                # handle case when a random user leave
                self.fake_update(left_chat_member=random_user, chat=chat),
                # handle case when channel doesn't exists
                self.fake_update(left_chat_member=bot_user, chat=not_added_chat),
            ]
        )

        context = MagicMock()
        context.bot = self.bot

        # handle case when channel doesn't exists
        command.handler(self.bot.get_updates().pop(), context)
        self.assertTrue(Channel.query.filter_by(chat_id="1").one_or_none())

        # handle case when a random user leave
        command.handler(self.bot.get_updates().pop(), context)
        self.assertTrue(Channel.query.filter_by(chat_id="1").one_or_none())

        # handle case when the bot leave (channel get removed from the database)
        command.handler(self.bot.get_updates().pop(), context)
        self.assertFalse(Channel.query.filter_by(chat_id="1").one_or_none())


if __name__ == "__main__":
    unittest.main()
