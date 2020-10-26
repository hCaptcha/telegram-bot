import unittest
from unittest.mock import MagicMock, call

from app.extensions import db
from app.lib.handlers.stats import StatsCommand
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
        command = StatsCommand()
        self.bot.get_updates = MagicMock(return_value=[self.fake_update()])
        command.reply_stats = MagicMock()
        update_event = self.bot.get_updates().pop()
        update_event.message.reply_text = MagicMock(return_value=None)

        context = MagicMock()
        context.bot = self.bot
        command.can_get_stats = MagicMock(return_value=True)
        command.handler(update_event, context)

        # case when there is no bot/human in the channel
        command.reply_stats.assert_called_with(update_event.message, 0.0, 0, 0.0, 0)

        # Create required db records for calculating stats
        channel = Channel.query.filter_by(chat_id="1").first()
        random_human_1 = Human(user_id="3", user_name="tt")
        random_human_2 = Human(user_id="4", user_name="tt")
        random_bot_1 = Bot(user_id="5", user_name="tt")
        random_bot_2 = Bot(user_id="6", user_name="tt")
        db.session.add(random_human_1)
        db.session.flush()
        human1_id = random_human_1.id
        db.session.add(random_human_2)
        db.session.flush()
        human2_id = random_human_2.id
        db.session.add(random_bot_1)
        db.session.flush()
        bot1_id = random_bot_1.id
        db.session.add(random_bot_2)
        db.session.flush()
        bot2_id = random_bot_2.id
        # Add memberships
        db.session.query(HumanChannelMember).delete()
        db.session.query(BotChannelMember).delete()
        db.session.add(HumanChannelMember(human_id=human1_id, channel_id=channel.id))
        db.session.add(HumanChannelMember(human_id=human2_id, channel_id=channel.id))
        db.session.add(BotChannelMember(bot_id=bot1_id, channel_id=channel.id))
        db.session.add(BotChannelMember(bot_id=bot2_id, channel_id=channel.id))

        command.handler(update_event, context)
        # can get stats
        command.reply_stats.assert_called_with(update_event.message, 50.0, 2, 50.0, 2)

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
