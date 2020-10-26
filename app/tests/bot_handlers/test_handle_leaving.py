import unittest
from unittest.mock import MagicMock

from base import TestBotHandlersBase
from telegram import Chat, User

from app.extensions import db
from app.lib.handlers.left_chat_member import LeftChatMemberFilter
from app.models import (Bot, BotChannelMember, Channel, Human,
                        HumanChannelMember)


class TestHandler(TestBotHandlersBase):
    def test(self):
        command = LeftChatMemberFilter()
        chat = Chat(id=1, type="supergroup", title="channel 1")
        not_added_chat = Chat(id=2, type="supergroup", title="channel 2")

        channel = Channel.query.filter_by(chat_id="1").first()
        random_user_1 = User(id=111, first_name="tt", user_name="test", is_bot=False)
        random_user_2 = User(id=112, first_name="tt", user_name="test1", is_bot=False)
        random_bot_1 = User(id=11, first_name="tt", user_name="test2", is_bot=True)
        random_bot_2 = User(id=12, first_name="tt", user_name="test3", is_bot=True)

        # Create required db records
        human_1 = Human(user_id="111", user_name="tt")
        human_2 = Human(user_id="112", user_name="tt")
        bot_1 = Bot(user_id="11", user_name="tt")
        bot_2 = Bot(user_id="12", user_name="tt")
        db.session.add(human_1)
        db.session.flush()
        human1_id = human_1.id
        db.session.add(human_2)
        db.session.flush()
        human2_id = human_2.id
        db.session.add(bot_1)
        db.session.flush()
        bot1_id = bot_1.id
        db.session.add(bot_2)
        db.session.flush()
        bot2_id = bot_2.id
        # Add memberships
        db.session.add(HumanChannelMember(human_id=human1_id, channel_id=channel.id))
        db.session.add(HumanChannelMember(human_id=human2_id, channel_id=channel.id))
        db.session.add(BotChannelMember(bot_id=bot1_id, channel_id=channel.id))
        db.session.add(BotChannelMember(bot_id=bot2_id, channel_id=channel.id))

        bot_user = self.bot

        self.bot.get_updates = MagicMock(
            return_value=[
                # handle case when the bot leave
                self.fake_update(left_chat_member=bot_user, chat=chat),
                # handle case when a random bot leave
                self.fake_update(left_chat_member=random_bot_1, chat=chat),
                # handle case when a random user leave
                self.fake_update(left_chat_member=random_user_1, chat=chat),
                # handle case when channel doesn't exists
                self.fake_update(left_chat_member=bot_user, chat=not_added_chat),
            ]
        )

        context = MagicMock()
        context.bot = self.bot

        # handle case when channel doesn't exists
        command.handler(self.bot.get_updates().pop(), context)
        self.assertTrue(Channel.query.filter_by(chat_id="1").one_or_none())

        # handle case when a random user leave
        command.handler(self.bot.get_updates().pop(), context)
        self.assertTrue(Channel.query.filter_by(chat_id="1").one_or_none())
        self.assertFalse(
            HumanChannelMember.query.filter_by(
                channel_id=channel.id, human_id=human1_id
            ).one_or_none()
        )
        self.assertTrue(
            HumanChannelMember.query.filter_by(
                channel_id=channel.id, human_id=human2_id
            ).one_or_none()
        )

        # handle case when a random bot leave
        command.handler(self.bot.get_updates().pop(), context)
        self.assertTrue(Channel.query.filter_by(chat_id="1").one_or_none())
        self.assertFalse(
            BotChannelMember.query.filter_by(
                channel_id=channel.id, bot_id=bot1_id
            ).one_or_none()
        )
        self.assertTrue(
            BotChannelMember.query.filter_by(
                channel_id=channel.id, bot_id=bot2_id
            ).one_or_none()
        )

        # handle case when the bot leave (channel get removed from the database)
        command.handler(self.bot.get_updates().pop(), context)
        self.assertFalse(Channel.query.filter_by(chat_id="1").one_or_none())
        self.assertFalse(
            HumanChannelMember.query.filter_by(
                channel_id=channel.id, human_id=human2_id
            ).one_or_none()
        )
        self.assertFalse(
            BotChannelMember.query.filter_by(
                channel_id=channel.id, bot_id=bot2_id
            ).one_or_none()
        )


if __name__ == "__main__":
    unittest.main()
