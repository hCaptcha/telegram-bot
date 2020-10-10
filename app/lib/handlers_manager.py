from telegram.ext import CommandHandler, Filters, MessageHandler

from app.extensions import db
from app.lib.handlers.base import BaseHandler
from app.lib.handlers.chat_created import ChatCreatedFilter
from app.lib.handlers.help import HelpCommand
from app.lib.handlers.left_chat_member import LeftChatMemberFilter
from app.lib.handlers.migrate import MigrateFilter
from app.lib.handlers.new_chat_members import NewChatMembersFilter
from app.lib.handlers.restrict import RestrcitCommand
from app.lib.handlers.start import StartCommand
from app.lib.handlers.stats import StatsCommand
from app.lib.handlers.unknown import UnknownCommand
from app.models import Human


class HandlersManager(BaseHandler):
    def __init__(self, dispatcher, app):
        super().__init__(app)
        self.dispatcher = dispatcher
        self.app = app

    def register(self):
        handlers = [
            MessageHandler(
                Filters.status_update.new_chat_members,
                NewChatMembersFilter(self.app).handler,
            ),
            MessageHandler(
                Filters.status_update.chat_created, ChatCreatedFilter(self.app).handler
            ),
            MessageHandler(
                Filters.status_update.migrate, MigrateFilter(self.app).handler
            ),
            MessageHandler(
                Filters.status_update.left_chat_member,
                LeftChatMemberFilter(self.app).handler,
            ),
            CommandHandler("start", StartCommand(self.app).handler, pass_args=True),
            CommandHandler("hi", StartCommand(self.app).handler, pass_args=True),
            CommandHandler("help", HelpCommand(self.app).handler),
            CommandHandler("restrict", RestrcitCommand(self.app).handler),
            CommandHandler("stats", StatsCommand(self.app).handler),
            MessageHandler(Filters.command, UnknownCommand(self.app).handler),
        ]

        for handler in handlers:
            self.dispatcher.add_handler(handler)
