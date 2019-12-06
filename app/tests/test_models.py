import unittest
from app.models import Human
from test_helpers import BaseCase


class TestModels(BaseCase):
    def test_human_model_defaults(self):
        h = Human.query.filter_by(user_id="1", user_name="joe").one_or_none()

        self.assertFalse(h.verified)
        self.assertEqual(0, h.attempts)
        self.assertIsNone(h.verification_date)
