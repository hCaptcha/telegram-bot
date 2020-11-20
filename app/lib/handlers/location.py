from geopy.geocoders import Nominatim
from telegram import Update
from telegram.ext import CallbackContext

from app.extensions import db
from app.lib.handlers.base import BaseHandler, app_context, catch_error
from app.models import (
    Bot,
    BotChannelMember,
    Channel,
    Human,
    HumanChannelMember,
)


class LocationFilter(BaseHandler):
    @app_context
    @catch_error
    def handler(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        message = None
        if update.edited_message:
            message = update.edited_message
        else:
            message = update.message
        user_id = message.from_user.id
        current_loc = (message.location.latitude, message.location.longitude)

        channel_name = None
        if context.args:
            channel_name = " ".join(context.args)

        human = Human.query.filter(
            Human.user_id == str(user_id),
        ).one_or_none()
        if human is not None:
            # Update location
            geolocator = Nominatim(user_agent="hcaptcha-bot")
            human.lat = current_loc[0]
            human.lng = current_loc[1]
            print(human.lat, human.lng)
            location = geolocator.reverse((human.lat, human.lng))
            human.country_code = location.raw["address"]["country_code"]
            db.session.commit()
