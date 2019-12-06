import unittest
from telegram import User, ChatPermissions
from unittest.mock import MagicMock, call

from base import TestBotHandlersBase
from app.models import Channel, Human
from app.extensions import db
from app.lib.handlers.start import StartCommand


class TestHandler(TestBotHandlersBase):
    def test(self):
        command = StartCommand()
        human = Human.query.filter_by(user_id="1").one_or_none()
        user = User(id=1, first_name="Joe", last_name="Doe", is_bot=False)
        self.bot.get_updates = MagicMock(return_value=[self.fake_update()])
        self.bot.send_message = MagicMock(return_value=None)
        self.bot.restrict_chat_member = MagicMock(return_value=None)
        update_event = self.bot.get_updates().pop()

        # when callback_chat_id is not set, user is verified
        human.verified = True
        db.session.commit()

        context = MagicMock()
        context.bot = self.bot
        context.args = []

        command.handler(update_event, context)

        self.bot.restrict_chat_member.assert_not_called()
        self.bot.send_message.assert_called()
        self.assertEqual(
            self.bot.send_message.call_args[1],
            {"chat_id": 1, "text": "You're already verified as human."},
        )

        self.bot.send_message.reset_mock()
        self.bot.restrict_chat_member.reset_mock()

        # when callback_chat_id is not set, user is not verified
        human.verified = False
        db.session.commit()

        command.handler(update_event, context)

        self.bot.restrict_chat_member.assert_not_called()
        self.bot.send_message.assert_called()
        self.assertEqual(self.bot.send_message.call_count, 2)
        self.bot.send_message.assert_has_calls(
            [
                call(chat_id=1, text="Hi, I'm a bot that helps verify you're human :)"),
                call(
                    1,
                    "Please click the following link to verify yourself before you're allowed to chat.**",
                    parse_mode="Markdown",
                    reply_markup='{"inline_keyboard": [[{"text": "Go to verification page", "url": "http://127.0.0.1:8000/1/1/Joe Doe?callback_chat_id=None"}]]}',
                ),
            ]
        )

        self.bot.send_message.reset_mock()
        self.bot.restrict_chat_member.reset_mock()

        # when callback_chat_id is set, user is verified
        human.verified = True
        db.session.commit()

        context.args = ["1234"]
        command.handler(update_event, context)

        self.bot.send_message.assert_called()
        self.assertEqual(self.bot.send_message.call_count, 1)
        self.bot.send_message.assert_has_calls(
            [
                call(
                    chat_id=1,
                    text="You're already verified as human, you'll be able to chat in the group",
                )
            ]
        )

        self.bot.restrict_chat_member.assert_called()
        self.assertEqual(self.bot.restrict_chat_member.call_count, 1)
        self.bot.restrict_chat_member.assert_has_calls(
            [
                call(
                    "1234",
                    1,
                    permissions=ChatPermissions(
                        can_send_messages=True,
                        can_send_media_messages=True,
                        can_send_other_messages=True,
                    ),
                )
            ]
        )

        self.bot.send_message.reset_mock()
        self.bot.restrict_chat_member.reset_mock()

        # when callback_chat_id is set, user is not verified
        human.verified = False
        db.session.commit()

        context.args = ["1234"]
        command.handler(update_event, context)

        self.bot.restrict_chat_member.assert_not_called()
        self.bot.send_message.assert_called()
        self.assertEqual(self.bot.send_message.call_count, 2)
        self.bot.send_message.assert_has_calls(
            [
                call(chat_id=1, text="Hi, I'm a bot that helps verify you're human :)"),
                call(
                    1,
                    "Please click the following link to verify yourself before you're allowed to chat.**",
                    parse_mode="Markdown",
                    reply_markup='{"inline_keyboard": [[{"text": "Go to verification page", "url": "http://127.0.0.1:8000/1/1/Joe Doe?callback_chat_id=1234"}]]}',
                ),
            ]
        )


if __name__ == "__main__":
    unittest.main()
