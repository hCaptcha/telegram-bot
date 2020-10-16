import unittest
from unittest.mock import MagicMock

from app.lib.handlers_manager import HandlersManager


class TestHandlersManager:
    def test_register(self):
        dispatcher = MagicMock(return_value=None)
        dispatcher.add_handler = MagicMock(return_value=None)
        handlers_manager = HandlersManager(dispatcher, None)

        handlers_manager.register()

        dispatcher.add_handler.assert_called()


if __name__ == "__main__":
    unittest.main()
