import unittest
from unittest.mock import MagicMock, call, patch

from telegram import ChatPermissions, User

from app.tests.test_helpers import AttrDict
from app.extensions import db
from app.lib.handlers.new_chat_members import NewChatMembersFilter
from app.models import (
    Bot,
    BotChannelMember,
    Channel,
    Human,
    HumanChannelMember,
)
from base import TestBotHandlersBase


class TestHandler(TestBotHandlersBase):
    def test(self):
        command = NewChatMembersFilter()
        self.bot.bot = MagicMock(return_value=AttrDict({"id": 123}))
        self.bot.get_my_commands = MagicMock(return_value=None)
        self.bot.get_me = MagicMock(return_value={"is_bot": True, "username": "test"})
        self.bot.restrict_chat_member = MagicMock(return_value=None)
        command.send_bot_link = MagicMock(
            return_value={"message_id": "123", "chat": {"id": "123"}}
        )
        command.add_message_info = MagicMock(return_value=None)
        # when bot first join
        self.bot.get_updates = MagicMock(
            return_value=[self.fake_update(new_chat_members=[self.bot])]
        )
        update_event = self.bot.get_updates().pop()
        context = MagicMock()
        context.bot = self.bot
        command.handle_invitation = MagicMock(return_value=None)

        with patch(
            "app.lib.handlers.chat_created.ChatCreatedFilter.handler", return_value=None
        ) as mock_handler:
            command.handler(update_event, context)
            mock_handler.assert_called()
            self.assertEqual(mock_handler.call_count, 1)
            self.bot.restrict_chat_member.assert_not_called()
            command.send_bot_link.assert_not_called()

        # when a user joins and we can't restrict
        user = User(id=101, first_name="tt", username="test", is_bot=False)
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
            self.assertTrue("INFO:bot:user: 101 is already verified" in cm.output)
            self.bot.restrict_chat_member.assert_not_called()
            command.send_bot_link.assert_not_called()

        # when a user joins and they aren't verified
        command.is_verified = MagicMock(return_value=False)

        # First update the channel
        chan = Channel.query.filter_by(chat_id="1").first()
        chan.restrict = True
        db.session.commit()
        command.handler(update_event, context)
        # This must create new Human & HumanChannelMember records in the db
        new_human = db.session.query(Human).filter(Human.user_id == "101").one()
        assert new_human is not None
        new_human_channel_member = (
            db.session.query(HumanChannelMember)
            .filter(
                HumanChannelMember.human_id == new_human.id,
                HumanChannelMember.channel_id == 1,
            )
            .one()
        )
        assert new_human_channel_member is not None

        self.bot.restrict_chat_member.assert_called()
        command.send_bot_link.assert_called()
        command.add_message_info.assert_called_with("123", "123", 101)
        self.assertEqual(self.bot.restrict_chat_member.call_count, 1)
        self.bot.restrict_chat_member.assert_has_calls(
            [
                call(
                    1,
                    101,
                    permissions=ChatPermissions(
                        can_send_messages=False,
                        can_send_media_messages=False,
                        can_send_other_messages=False,
                    ),
                )
            ]
        )

        # when a bot joins and they aren't verified
        user = User(id=102, first_name="bot1", username="testbot", is_bot=True)
        self.bot.get_updates = MagicMock(
            return_value=[self.fake_update(new_chat_members=[user])]
        )
        update_event = self.bot.get_updates().pop()
        command.handler(update_event, context)
        # This must create new Bot & BotChannelMember records in the db
        new_bot = db.session.query(Bot).filter(Bot.user_id == "102").one()
        assert new_bot is not None
        new_bot_channel_member = (
            db.session.query(BotChannelMember)
            .filter(
                BotChannelMember.bot_id == new_bot.id, BotChannelMember.channel_id == 1
            )
            .one()
        )
        assert new_bot_channel_member is not None

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
