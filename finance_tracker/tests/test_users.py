import unittest
import os
from finance_tracker.users import UserManager

class TestUserManager(unittest.TestCase):
    def setUp(self):
        self.manager = UserManager()
        self.data_file = "users.json"
        if os.path.exists(self.data_file):
            os.remove(self.data_file)

    def test_register_user(self):
        self.manager.register_user("testuser", "password123", "test@example.com")
        self.assertIn("testuser", self.manager.users)
        self.assertEqual(self.manager.users["testuser"].email, "test@example.com")

    def test_register_invalid_user(self):
        with self.assertRaises(ValueError):
            self.manager.register_user("", "password123", "test@example.com")
        with self.assertRaises(ValueError):
            self.manager.register_user("testuser", "short", "test@example.com")
        with self.assertRaises(ValueError):
            self.manager.register_user("testuser", "password123", "invalid_email")

    def test_authenticate_user(self):
        if "testuser" not in self.manager.users:
            self.manager.register_user("testuser", "password123", "test@example.com")
        self.assertTrue(self.manager.authenticate_user("testuser", "password123"))
        self.assertFalse(self.manager.authenticate_user("testuser", "wrongpass"))

    def test_update_user(self):
        if "testuser" not in self.manager.users:
            self.manager.register_user("testuser", "password123", "test@example.com")
        self.assertTrue(self.manager.update_user("testuser", email="new@example.com", 
                                               preferences={"currency": "EUR"}))
        user = self.manager.get_user("testuser")
        self.assertEqual(user["email"], "new@example.com")
        self.assertEqual(user["preferences"]["currency"], "EUR")

    def test_delete_user(self):
        if "testuser" not in self.manager.users:
            self.manager.register_user("testuser", "password123", "test@example.com")
        self.assertTrue(self.manager.delete_user("testuser"))
        self.assertIsNone(self.manager.get_user("testuser"))