import unittest
from unittest.mock import MagicMock, call, patch

from base import TestBotHandlersBase
from app.lib.handlers.unknown import UnknownCommand


class TestHandler(TestBotHandlersBase):
    def test(self):
        command = UnknownCommand()
        self.bot.get_updates = MagicMock(
            return_value=[self.fake_update(text="/lorem ipsum")]
        )
        self.bot.send_message = MagicMock(return_value={"message_id":"123","chat":{"id":"123"}})

        context = MagicMock()
        context.bot = self.bot

        with patch("app.lib.handlers.help.HelpCommand.handler", return_value=None) as mock_handler:
            command.handler(self.bot.get_updates().pop(), context)

            mock_handler.assert_called()
            self.assertEqual(mock_handler.call_count, 1)

            self.bot.send_message.assert_called()
            self.assertEqual(self.bot.send_message.call_count, 1)
            self.bot.send_message.assert_has_calls(
                [
                    call(
                        chat_id=1,
                        text="Sorry, didn't recognize this command:\n/lorem ipsum",
                    )
                ]
            )


        self.bot.send_message.reset_mock()
        # command.add_message_info.reset_mock()
        self.bot.get_updates = MagicMock(
            return_value=[
                self.fake_update(
                    text="/lorem ipsum very very very very very very long string"
                )
            ]
        )

        context = MagicMock()
        context.bot = self.bot
        command.handler(self.bot.get_updates().pop(), context)

        self.bot.send_message.assert_has_calls(
            [
                call(
                    chat_id=1,
                    text="Sorry, didn't recognize this command:\n/lorem ipsum very very very ve...",
                )
            ]
        )


if __name__ == "__main__":
    unittest.main()
