import unittest
from unittest.mock import MagicMock, call

from telegram import Chat, User

from app.extensions import db
from app.lib.handlers.restrict import RestrcitCommand
from app.models import Channel
from app.tests.test_helpers import AttrDict
from base import TestBotHandlersBase


class TestHandler(TestBotHandlersBase):
    def test(self):
        command = RestrcitCommand()

        update_event = self.fake_update()
        reply_text = update_event.message.reply_text = MagicMock(return_value=None)
        channel = Channel.query.filter_by(chat_id="1").first()
        context = MagicMock()
        self.bot.bot = MagicMock(return_value=AttrDict({"id": 123}))
        self.bot.get_my_commands = MagicMock(return_value=None)
        self.bot.get_me = MagicMock(return_value={"is_bot": True, "username": "test"})
        context.bot = self.bot
        context.args = []

        # no arguments case
        command.handler(update_event, context)

        db.session.refresh(channel)
        self.assertFalse(channel.restrict)
        reply_text.assert_called()
        self.assertEqual(reply_text.call_count, 1)
        reply_text.assert_has_calls([call("Usage: /restrict <channel>")])

        reply_text.reset_mock()

        # channel is none
        context.args = ["test ab"]
        command.handler(update_event, context)

        db.session.refresh(channel)
        self.assertFalse(channel.restrict)
        reply_text.assert_called()
        self.assertEqual(reply_text.call_count, 1)
        reply_text.assert_has_calls(
            [
                call(
                    "test ab is not registered to the bot, please invite me there first."
                )
            ]
        )

        reply_text.reset_mock()

        # user is not an admin
        command.is_admin_on_channel = MagicMock(return_value=False)

        context.args = ["test"]
        command.handler(update_event, context)

        db.session.refresh(channel)
        self.assertFalse(channel.restrict)
        reply_text.assert_called()
        self.assertEqual(reply_text.call_count, 1)
        reply_text.assert_has_calls(
            [call("You must be an admin on <test> to restrict it.")]
        )

        reply_text.reset_mock()

        # channel is already restricted
        channel.restrict = True
        db.session.commit()
        command.is_admin_on_channel = MagicMock(return_value=True)

        context.args = ["test"]
        command.handler(update_event, context)

        db.session.refresh(channel)
        self.assertTrue(channel.restrict)
        reply_text.assert_called()
        self.assertEqual(reply_text.call_count, 1)
        reply_text.assert_has_calls([call("<test> is already restricted.")])

        channel.restrict = False
        db.session.commit()
        reply_text.reset_mock()

        # can't restrict channel
        command.can_restrict_channel = MagicMock(return_value=False)

        context.args = ["test"]
        command.handler(update_event, context)

        db.session.refresh(channel)
        self.assertFalse(channel.restrict)
        reply_text.assert_called()
        self.assertEqual(reply_text.call_count, 1)
        reply_text.assert_has_calls(
            [
                call(
                    "test must be a supergroup and the bot must be have admin permissions"
                )
            ]
        )

        reply_text.reset_mock()

        # can restrict channel
        command.can_restrict_channel = MagicMock(return_value=True)

        context.args = ["test"]
        command.handler(update_event, context)

        db.session.refresh(channel)
        self.assertTrue(channel.restrict)
        reply_text.assert_called()
        self.assertEqual(reply_text.call_count, 1)
        reply_text.assert_has_calls(
            [
                call(
                    "New users joining <test> will be asked to verify themselves before being able to send new messages"
                )
            ]
        )

        reply_text.reset_mock()

    def test_is_admin_on_channel(self):
        command = RestrcitCommand()
        chat = Chat(id=1, type="supergroup", title="channel 1")
        chat.get_administrators = MagicMock(
            return_value=[
                AttrDict({"user": AttrDict({"id": 1})}),
                AttrDict({"user": AttrDict({"id": 2})}),
            ]
        )
        self.bot.get_chat = MagicMock(return_value=chat)

        # is not admin
        self.assertFalse(command.is_admin_on_channel(self.bot, chat.id, 3))

        # is admin
        self.assertTrue(command.is_admin_on_channel(self.bot, chat.id, 1))


if __name__ == "__main__":
    unittest.main()
