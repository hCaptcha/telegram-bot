from telegram import Update
from telegram.ext import CallbackContext

from app.extensions import db
from app.lib.handlers.base import BaseHandler, app_context
from app.models import (
    Bot,
    BotChannelMember,
    Channel,
    Human,
    HumanChannelMember,
)


class StatsCommand(BaseHandler):
    @app_context
    def handler(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id

        channel_name = None
        if context.args:
            channel_name = " ".join(context.args)
        if self.can_get_stats(
            context.bot, chat_id, update.message.from_user.id, channel_name
        ):

            num_bots = (
                db.session.query(BotChannelMember)
                .join(Channel)
                .filter(Channel.chat_id == str(update.message.chat_id))
                .count()
            )
            num_humans = (
                db.session.query(HumanChannelMember)
                .join(Channel)
                .filter(Channel.chat_id == str(update.message.chat_id))
                .count()
            )
            num_all_user = num_humans + num_bots
            if num_all_user == 0:
                percent_humans = 0
                percent_bots = 0
            else:
                percent_humans = num_humans / float(num_all_user) * 100
                percent_bots = num_bots / float(num_all_user) * 100
            self.reply_stats(
                update.message, percent_humans, num_humans, percent_bots, num_bots
            )

        else:
            update.message.reply_text("You don't have permission to get stats")

    def can_get_stats(self, bot, chat_id, user_id, channel_name):
        if not channel_name:
            return True

        channel = Channel.query.filter(Channel.name == channel_name).one_or_none()
        if not channel:
            return False

        user_status = bot.get_chat_member(chat_id, user_id).status
        return user_status == "admin"

    def reply_stats(self, message, percent_humans, num_humans, percent_bots, num_bots):
        message.reply_text(
            "Current channel stats:\nHumans: {:.2f}%({})\nBots: {:.2f}%({})".format(
                percent_humans, num_humans, percent_bots, num_bots
            )
        )
