import unittest
from unittest.mock import MagicMock, call

from app.lib.handlers.help import HelpCommand
from base import TestBotHandlersBase


class TestHandler(TestBotHandlersBase):
    def test(self):
        command = HelpCommand()
        self.bot.send_message = MagicMock(return_value=None)

        context = MagicMock()
        context.bot = self.bot
        command.handler(self.fake_update(), context)

        self.bot.send_message.assert_called()
        self.assertEqual(self.bot.send_message.call_count, 1)
        self.bot.send_message.assert_has_calls(
            [
                call(
                    chat_id=1,
                    parse_mode="Markdown",
                    text="\nAvailable commands:\n\n/hi - check your status or verify yourself\n/restrict <super_group> - restrict newly joined users in <super_group>. bot should have admin permissions.\n/stats - show statistics about humans/bots in channels\n",
                )
            ]
        )


if __name__ == "__main__":
    unittest.main()
