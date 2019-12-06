import unittest
from unittest.mock import MagicMock, call

from base import TestBotHandlersBase
from app.lib.handlers.stats import StatsCommand


class TestHandler(TestBotHandlersBase):
    def test(self):
        command = StatsCommand()
        self.bot.get_updates = MagicMock(return_value=[self.fake_update()])
        update_event = self.bot.get_updates().pop()
        update_event.message.reply_text = MagicMock(return_value=None)

        context = MagicMock()
        context.bot = self.bot
        # no args passed
        # TODO
        command.handler(update_event, context)

        # can get stats
        # TODO

        # can't get stats
        command.can_get_stats = MagicMock(return_value=False)

        command.handler(update_event, context)

        update_event.message.reply_text.assert_called()
        self.assertEqual(update_event.message.reply_text.call_count, 1)
        update_event.message.reply_text.assert_has_calls(
            [call("You don't have permission to get stats")]
        )


if __name__ == "__main__":
    unittest.main()
