import unittest
from unittest.mock import MagicMock

from telegram import Chat, User

from app.extensions import db
from app.lib.handlers.migrate import MigrateFilter
from app.models import Channel
from base import TestBotHandlersBase


class TestHandler(TestBotHandlersBase):
    def test(self):
        command = MigrateFilter()
        chat = Chat(id=2, type="private")
        new_chat = Chat(id=3, type="private")

        channel = Channel(chat_id="2", name="test")
        db.session.add(channel)
        db.session.commit()

        self.bot.get_updates = MagicMock(
            return_value=[
                self.fake_update(migrate_from_chat_id=2, chat=new_chat),
                self.fake_update(migrate_from_chat_id=3, chat=new_chat),
                self.fake_update(migrate_to_chat_id=3, chat=chat),
            ]
        )
        context = MagicMock()
        context.bot = self.bot

        command.handler(self.bot.get_updates().pop(), context)

        db.session.expire(channel)
        db.session.refresh(channel)

        self.assertEqual(channel.chat_id, "2")

        with self.assertLogs("bot", level="INFO") as cm:
            command.handler(self.bot.get_updates().pop(), context)
            self.assertEqual(
                cm.output,
                [
                    "ERROR:bot:Unable to find a channel that should exists: original_chat_id: 3, new_chat_id: 3"
                ],
            )

        db.session.expire(channel)
        db.session.refresh(channel)

        self.assertEqual(channel.chat_id, "2")

        command.handler(self.bot.get_updates().pop(), context)

        db.session.expire(channel)
        db.session.refresh(channel)

        self.assertEqual(channel.chat_id, "3")


if __name__ == "__main__":
    unittest.main()
