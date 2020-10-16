import json

from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from app.config import get_active_config
from app.lib.handlers.base import BaseHandler, app_context


class StartCommand(BaseHandler):
    @app_context
    def handler(self, update: Update, context: CallbackContext):
        self.logger.info(f"called handle_start with arguments: {context.args}")

        # We have 2 cases for a user calling /start directly:
        # 1- If a user directly message the bot just to verify themselves
        # 2- If the user is redirected from a certain group to the bot to verification
        # For case 1, we'll send the challenge and tell them if they pass
        # For case 2, additional to case 1 steps, we'll remove the restrictions for the passed callback_chat_id

        try:
            callback_chat_id = context.args[0]
        except IndexError:
            callback_chat_id = None

        if self.is_verified(update.message.from_user.id):
            if callback_chat_id:
                context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text="You're already verified as human, you'll be able to chat in the group",
                )
                self.remove_restrictions(
                    context.bot,
                    callback_chat_id,
                    update.message.from_user.id,
                    update.message.from_user.name,
                )
            else:
                context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text="You're already verified as human.",
                )
        else:
            res = context.bot.send_message(
                chat_id=update.message.chat_id,
                text="Hi, I'm a bot that helps verify you're human :)",
            )
            self.add_message_info(
                res["message_id"], res["chat"]["id"], update.message.from_user.id
            )
            self.send_challenge(
                context.bot,
                update.message.chat_id,
                update.message.from_user,
                callback_chat_id=callback_chat_id,
            )

    def send_challenge(self, bot, chat_id, user, callback_chat_id=None):
        res = bot.send_message(
            chat_id,
            f"Please click the following link to verify yourself before you're allowed to chat.**",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {
                                "text": "Go to verification page",
                                "url": f"{get_active_config().APP_URL}{chat_id}/{user.id}/{user.name}?callback_chat_id={callback_chat_id}",
                            }
                        ]
                    ]
                }
            ),
        )
        self.add_message_info(res["message_id"], res["chat"]["id"], user.id)
