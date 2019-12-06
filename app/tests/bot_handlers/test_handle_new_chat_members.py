import unittest
from telegram import User, ChatPermissions
from unittest.mock import MagicMock, call, patch

from base import TestBotHandlersBase
from app.lib.handlers.new_chat_members import NewChatMembersFilter
from app.models import Channel
from app.extensions import db


class TestHandler(TestBotHandlersBase):
    def test(self):
        command = NewChatMembersFilter()
        self.bot.restrict_chat_member = MagicMock(return_value=None)
        command.send_bot_link = MagicMock(return_value=None)
        # when bot first join
        self.bot.get_updates = MagicMock(
            return_value=[self.fake_update(new_chat_members=[self.bot])]
        )
        update_event = self.bot.get_updates().pop()
        context = MagicMock()
        context.bot = self.bot
        command.handle_invitation = MagicMock(return_value=None)

        with patch('app.lib.handlers.chat_created.ChatCreatedFilter.handler', return_value=None) as mock_handler:
            command.handler(update_event, context)
            mock_handler.assert_called()
            self.assertEqual(mock_handler.call_count, 1)
            self.bot.restrict_chat_member.assert_not_called()
            command.send_bot_link.assert_not_called()

        # when a user joins and we can't restrict
        user = User(id=1, first_name="tt", user_name="test", is_bot=False)
        self.bot.get_updates = MagicMock(
            return_value=[self.fake_update(new_chat_members=[user])]
        )
        update_event = self.bot.get_updates().pop()
        command.can_restrict_channel = MagicMock(return_value=False)

        with self.assertLogs("bot", level="INFO") as cm:
            command.handler(update_event, context)

            self.assertTrue("INFO:bot:we can't restrict this chat: 1" in cm.output)
            self.bot.restrict_chat_member.assert_not_called()
            command.send_bot_link.assert_not_called()

        # when a user joins and we shouldn't restrict
        command.can_restrict_channel = MagicMock(return_value=True)
        command.should_restrict_channel = MagicMock(return_value=False)

        with self.assertLogs("bot", level="INFO") as cm:
            command.handler(update_event, context)

            self.assertTrue("INFO:bot:we shouldn't restrict this chat: 1" in cm.output)
            self.bot.restrict_chat_member.assert_not_called()
            command.send_bot_link.assert_not_called()

        # when a user joins and they are verified
        command.should_restrict_channel = MagicMock(return_value=True)
        command.is_verified = MagicMock(return_value=True)

        with self.assertLogs("bot", level="INFO") as cm:
            command.handler(update_event, context)
            self.assertTrue("INFO:bot:user: 1 is already verified" in cm.output)
            self.bot.restrict_chat_member.assert_not_called()
            command.send_bot_link.assert_not_called()

        # when a user joins and they aren't verified
        command.is_verified = MagicMock(return_value=False)

        command.handler(update_event, context)

        self.bot.restrict_chat_member.assert_called()
        command.send_bot_link.assert_called()
        self.assertEqual(self.bot.restrict_chat_member.call_count, 1)
        self.bot.restrict_chat_member.assert_has_calls(
            [
                call(
                    1,
                    1,
                    permissions=ChatPermissions(
                        can_send_messages=False,
                        can_send_media_messages=False,
                        can_send_other_messages=False,
                    ),
                )
            ]
        )

    def test_should_restrict_channel(self):
        command = NewChatMembersFilter()
        channel = Channel.query.filter_by(chat_id="1").first()
        channel.restrict = True

        db.session.commit()

        self.assertTrue(command.should_restrict_channel(channel.chat_id))

        channel.restrict = False

        db.session.commit()

        self.assertFalse(command.should_restrict_channel(channel.chat_id))


if __name__ == "__main__":
    unittest.main()
