import hashlib
import json
import os
from typing import Dict, Optional
from datetime import datetime
import re

class User:
    """Represents a user profile."""
    def __init__(self, username: str, password: str, email: str, created_at: str = None):
        self.username = username.strip()
        self.password_hash = self._hash_password(password)
        self.email = email.strip()
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.preferences = {"currency": "USD", "language": "en"}

    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def to_dict(self) -> Dict:
        """Convert user to dictionary."""
        return {
            "username": self.username,
            "password_hash": self.password_hash,
            "email": self.email,
            "created_at": self.created_at,
            "preferences": self.preferences
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        """Create user from dictionary."""
        user = cls(data["username"], "", data["email"], data["created_at"])
        user.password_hash = data["password_hash"]
        user.preferences = data["preferences"]
        return user

class UserManager:
    """Manages user authentication and profiles."""
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.data_file = "users.json"
        self._load_users()

    def validate_email(self, email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def register_user(self, username: str, password: str, email: str) -> bool:
        """Register a new user."""
        if not username or not password or not email:
            raise ValueError("Username, password, and email cannot be empty")
        if username in self.users:
            raise ValueError("Username already exists")
        if not self.validate_email(email):
            raise ValueError("Invalid email format")
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        self.users[username] = User(username, password, email)
        self._save_users()
        return True

    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate a user."""
        if username in self.users:
            user = self.users[username]
            return user.password_hash == hashlib.sha256(password.encode()).hexdigest()
        return False

    def update_user(self, username: str, email: str = None, password: str = None,
                   preferences: Dict = None) -> bool:
        """Update user profile."""
        if username not in self.users:
            return False
        user = self.users[username]
        if email is not None:
            if not self.validate_email(email):
                raise ValueError("Invalid email format")
            user.email = email.strip()
        if password is not None:
            if len(password) < 8:
                raise ValueError("Password must be at least 8 characters")
            user.password_hash = user._hash_password(password)
        if preferences is not None:
            user.preferences.update(preferences)
        self._save_users()
        return True

    def delete_user(self, username: str) -> bool:
        """Delete a user."""
        if username in self.users:
            del self.users[username]
            self._save_users()
            return True
        return False

    def get_user(self, username: str) -> Optional[Dict]:
        """Retrieve user profile."""
        user = self.users.get(username)
        return user.to_dict() if user else None

    def _save_users(self) -> None:
        """Save users to a JSON file."""
        with open(self.data_file, 'w') as f:
            json.dump({username: user.to_dict() for username, user in self.users.items()}, f, indent=2)

    def _load_users(self) -> None:
        """Load users from a JSON file."""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.users = {username: User.from_dict(user_data) for username, user_data in data.items()}
        except FileNotFoundError:
            self.users = {}