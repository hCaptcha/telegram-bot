import unittest
from unittest.mock import MagicMock

from telegram import Chat, User

from app.lib.handlers.chat_created import ChatCreatedFilter
from app.models import Channel
from base import TestBotHandlersBase


class TestHandler(TestBotHandlersBase):
    def test(self):
        command = ChatCreatedFilter()
        new_channel_chat = Chat(id=3, type="private", title="new_channel")
        invitee_user = User(id=1, first_name="tt", user_name="test", is_bot=False)

        self.bot.send_message = MagicMock(return_value=None)
        context = MagicMock()
        context.bot = self.bot
        command.handler(
            self.fake_update(
                chat=new_channel_chat,
                channel_chat_created=True,
                from_user=invitee_user,
            ),
            context,
        )

        self.assertTrue(
            Channel.query.filter_by(chat_id="3", name="new_channel").one_or_none()
        )
        self.bot.send_message.assert_called()
        self.assertEqual(
            self.bot.send_message.call_args[1],
            {
                "chat_id": 3,
                "text": "Hi, None invited me here to keep <new_channel> human! If you'd like to participate, just message me 'hi' to start. I'll remember you're human if we've spoken before :)",
            },
        )


if __name__ == "__main__":
    unittest.main()
