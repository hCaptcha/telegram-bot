from sqlalchemy import func
from telegram import Update
from telegram.ext import CallbackContext

from app.config import get_active_config
from app.extensions import db
from app.lib.handlers.base import BaseHandler, app_context, catch_error
from app.models import (
    Bot,
    BotChannelMember,
    Channel,
    Human,
    HumanChannelMember,
)


class StatsCommand(BaseHandler):
    @app_context
    @catch_error
    def handler(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id

        if self.can_get_stats(
            context.bot,
            chat_id,
            update.message.from_user.id,
            update.message.from_user.username,
        ):

            # count all humans/bots
            num_bots = db.session.query(Bot).count()
            num_humans = db.session.query(Human).count()
            num_all_user = num_humans + num_bots

            # init stats
            percent_bots = 0
            percent_humans = 0
            to_sorted_location = []

            if num_bots == 0:
                percent_bots = 0
            else:
                percent_bots = num_bots / float(num_all_user) * 100

            if num_humans == 0:
                percent_humans = 0
            else:
                percent_humans = num_humans / float(num_all_user) * 100
                count_per_country = (
                    db.session.query(Human.country_code, func.count(Human.id))
                    .group_by(Human.country_code)
                    .all()
                )

                # Find percent of each country for the entire pool
                percent_per_country = map(
                    lambda x: (
                        x[0] if x[0] is not None else "unknown",
                        (float(x[1]) / num_humans) * 100.0,
                    ),
                    count_per_country,
                )
                to_sorted_location = list(
                    map(
                        lambda x: "{}: {:.2f}%".format(x[0], x[1]),
                        sorted(percent_per_country, key=lambda item: item[0]),
                    )
                )

            self.reply_stats(
                update.message,
                percent_humans,
                num_humans,
                percent_bots,
                num_bots,
                to_sorted_location,
            )

        else:
            update.message.reply_text("You don't have permission to get stats")

    def can_get_stats(self, bot, chat_id, user_id, username):
        """
        Currently there is no way that we can find the bot owner from Telegram api.
        We can make use of https://core.telegram.org/bots/api#getchatadministrators, but
        that is not very practical because of too many Telegram calls to find authorized
        channels of this administrator!
        So we need to set this somewhere in configs.
        """
        # check if we are chatting directly with this bot
        if user_id == chat_id:
            return True
        return False

    def reply_stats(
        self,
        message,
        percent_humans,
        num_humans,
        percent_bots,
        num_bots,
        per_country_sorted,
    ):
        message.reply_text(
            "Current pool stats:\nHumans: {:.2f}%({})\nBots: {:.2f}%({})\nPercent of users, per country:\n{}".format(
                percent_humans,
                num_humans,
                percent_bots,
                num_bots,
                "\n".join(per_country_sorted),
            )
        )
