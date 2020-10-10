import unittest
from telegram import User
from unittest.mock import MagicMock

from base import TestBotHandlersBase
from app.tests.test_helpers import AttrDict
from app.lib.handlers.restrict import RestrcitCommand
from app.lib.handlers.new_chat_members import NewChatMembersFilter

class TestHandler(TestBotHandlersBase):
    def test(self):
        command = NewChatMembersFilter()
        user = User(id=1, first_name="Joe", last_name="Doe", is_bot=False)

        update_event = self.fake_update(new_chat_members=[user])
        context = MagicMock()
        context.bot = self.bot

        # mock handle_new_chat_members
        self.bot.restrict_chat_member = MagicMock(return_value=None)
        self.bot.send_message = MagicMock(return_value={"message_id":"1234","chat":{"id":"1234"}})
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

        command.handler(update_event, context)

        self.bot.restrict_chat_member.assert_called()
        self.bot.send_message.assert_called()
        command.add_message_info.assert_called_with("1234", "1234")
        
        # mock remove_restrictions
        command.remove_restrictions(
            self.bot,
            update_event.message.chat.id,
            update_event.message.from_user.id,
            update_event.message.from_user.name,
        )

        self.bot.restrict_chat_member.assert_called()
        self.bot.send_message.assert_called()
        command.add_message_info.assert_called_with("1234", "1234")


if __name__ == "__main__":
    unittest.main()
