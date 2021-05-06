import unittest
from unittest.mock import MagicMock

from telegram import User

from app.extensions import db
from app.lib.handlers.new_chat_members import NewChatMembersFilter
from app.lib.handlers.restrict import RestrcitCommand
from app.models import Channel
from app.tests.test_helpers import AttrDict
from base import TestBotHandlersBase


class TestHandler(TestBotHandlersBase):
    def test(self):
        command = NewChatMembersFilter()
        user = User(
            id=1111, first_name="Joe", last_name="Doe", username="joe_doe", is_bot=False
        )

        update_event = self.fake_update(new_chat_members=[user])
        context = MagicMock()
        context.bot = self.bot

        # mock handle_new_chat_members
        self.bot.bot = MagicMock(return_value=AttrDict({"id": 123}))
        self.bot.get_my_commands = MagicMock(return_value=None)
        self.bot.get_me = MagicMock(return_value={"is_bot": True, "username": "test"})
        self.bot.restrict_chat_member = MagicMock(return_value=None)
        self.bot.send_message = MagicMock(
            return_value={"message_id": "1234", "chat": {"id": "1234"}}
        )
        command.add_message_info = MagicMock(return_value=None)
        self.bot.get_chat = MagicMock(return_value=AttrDict({"type": "supergroup"}))
        self.bot.get_chat_member = MagicMock(
            return_value=AttrDict({"status": "administrator"})
        )
        command.handler(update_event, context)

        self.bot.get_chat.assert_called()
        self.bot.get_chat_member.assert_called()
        # Shouldn't restrict these users
        self.bot.restrict_chat_member.assert_not_called()
        self.bot.send_message.assert_not_called()
        command.add_message_info.assert_not_called()

        command.can_restrict_channel = MagicMock(return_value=True)
        command.should_restrict_channel = MagicMock(return_value=True)

        # First update the channel
        chan = Channel.query.filter_by(chat_id="1").first()
        chan.restrict = True
        db.session.commit()
        command.handler(update_event, context)

        self.bot.restrict_chat_member.assert_called()
        self.bot.send_message.assert_called()
        command.add_message_info.assert_called_with("1234", "1234", 1111)

        # mock remove_restrictions
        command.remove_restrictions(
            self.bot,
            update_event.message.chat.id,
            update_event.message.from_user.id,
            update_event.message.from_user.name,
        )

        self.bot.restrict_chat_member.assert_called()
        self.bot.send_message.assert_called()
        command.add_message_info.assert_called_with("1234", "1234", 1111)


if __name__ == "__main__":
    unittest.main()
