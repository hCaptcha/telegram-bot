import unittest
from app import create_app


class BasicTests(unittest.TestCase):
    def setUp(self):
        self.test_app = create_app("testing").test_client()

    def test_home_page(self):
        response = self.test_app.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Hcaptcha telegram verification", response.data.decode("utf-8"))

    def test_verification_page(self):
        response = self.test_app.get("/1/1/testUser")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Please solve the following captcha.", response.data.decode("utf-8")
        )


if __name__ == "__main__":
    unittest.main()
