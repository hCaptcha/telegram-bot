import unittest
from unittest.mock import MagicMock

from test_helpers import BaseCase

from app.config import app_config
from app.lib.bot import HCaptchaBot


class TestBot(BaseCase):
    def setUp(self):
        super().setUp()
        self.hCaptchaBot = HCaptchaBot(app_config["testing"].TELEGRAM_TOKEN)
        self.bot = self.hCaptchaBot.bot

    def test_is_bot(self):
        self.assertTrue(self.bot.get_me()["is_bot"])

    def test_username(self):
        self.assertEqual(
            self.bot.get_me()["username"], app_config["testing"].TELEGRAM_USERNAME
        )

    def test_run(self):
        self.hCaptchaBot.handlers_manager.register = MagicMock(return_value=None)
        self.hCaptchaBot.updater.start_polling = MagicMock(return_value=None)

        self.hCaptchaBot.run()

        self.hCaptchaBot.handlers_manager.register.assert_called()
        self.hCaptchaBot.updater.start_polling.assert_called()


if __name__ == "__main__":
    unittest.main()
