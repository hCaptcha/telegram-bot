import logging
from datetime import datetime
from queue import Queue
from threading import Thread

from telegram import Bot, Update
from telegram.ext import Dispatcher, Updater

from app.config import get_active_config, should_run_webhook
from app.lib.cleanup_worker import CleanupWorker
from app.lib.handlers_manager import HandlersManager

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)

logger = logging.getLogger("bot")

"""
  Decorator to wrap a function call with an app context. This is necessary because of each callback need to
  run within a context to access the database.
"""


class HCaptchaBot:
    def __init__(self, token, app=None):
        self.token = token
        self.app = app

        if should_run_webhook():
            self.bot = Bot(self.token)
            self.update_queue = Queue()
            self.dispatcher = Dispatcher(self.bot, self.update_queue, use_context=True)
        else:
            self.updater = Updater(self.token, use_context=True)

            self.bot = self.updater.bot
            self.update_queue = None
            self.dispatcher = self.updater.dispatcher

        self.handlers_manager = HandlersManager(self.dispatcher, self.app)
        self.worker = CleanupWorker(self.bot, self.app)

    def verify(self, *args):
        """
        Proxy function, for ease of use.
        """

        return self.handlers_manager.verify(self.bot, *args)

    def setup(self):
        """
        Called once when the app launches.
        """

        # set webhook
        if not should_run_webhook():
            return

        webhook_url = "{}{}".format(get_active_config().APP_URL, self.token)

        current_webhook_url = self.bot.get_webhook_info().url

        if current_webhook_url != webhook_url:
            logger.info(f"setting webhook url to: {webhook_url}")
            self.bot.set_webhook(webhook_url)

    def exit(self):
        """
        Called once when the app is about to exit.
        """

        if not should_run_webhook():
            return

        # clean up running threads
        self.update_queue.stop()
        self.dispatcher_thread.join()
        self.cleanup_worker_thread.join()
        self.dispatcher.stop()

    def _run_polling(self):
        self.handlers_manager.register()

        self.updater.start_polling()
        logger.info("polling...")

    def _run_webhook(self):
        self.handlers_manager.register()

        self.dispatcher_thread = Thread(target=self.dispatcher.start, name="dispatcher")
        self.dispatcher_thread.start()

    def _run_cleanup_worker(self):
        self.cleanup_worker_thread = Thread(
            target=self.worker.run, name="cleanup_worker"
        )
        self.cleanup_worker_thread.start()

    def run(self):
        try:
            if should_run_webhook():
                self._run_webhook()
            else:
                self._run_polling()
            # Run the cleanup worker in a seperate thread.
            self._run_cleanup_worker()
        except Exception as e:
            print(e)
