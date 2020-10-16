import unittest

from app.extensions import db
from app.models import Human, Channel, Message
from app import create_app


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


class BaseCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            self.create_fixtures()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def create_fixtures(self):
        human = Human(user_id="1", user_name="joe")
        channel = Channel(chat_id="1", name="test", restrict=False)
        message = Message(user_id="1", chat_id="1", message_id="1")

        db.session.add(human)
        db.session.add(channel)
        db.session.add(message)
        db.session.commit()
