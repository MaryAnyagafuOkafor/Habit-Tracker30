"""
TESTS - User Model
===================

Unit tests for the User domain model.

Test Categories:
    - User Creation
    - Password Management
    - Role Management
    - Account Management
    - Serialization
"""

from src.core.models.user import User


class TestUserCreation:
    """Tests for creating users."""

    def test_create_basic_user(self):
        user = User("john_doe", password="password123", email="john@email.com")
        assert user.username == "john_doe"
        assert user.password_hash is not None
        assert user.is_active is True
        assert user.role == "user"

    def test_create_admin_user(self):
        user = User("admin", password="password", role="admin")
        assert user.role == "admin"

    def test_create_guest_user(self):
        user = User("guest", password="guest123", role="guest")
        assert user.role == "guest"


class TestPasswordManagement:
    """Tests for password hashing and verification."""

    def test_password_hashing(self):
        user = User("john", password="secure_password")
        assert user.password_hash is not None
        assert user.password_hash != "secure_password"

    def test_verify_correct_password(self):
        user = User("john", password="secure_password")
        assert user.verify_password("secure_password") is True

    def test_verify_incorrect_password(self):
        user = User("john", password="secure_password")
        assert user.verify_password("wrong_password") is False

    def test_set_new_password(self):
        user = User("john", password="old_password")
        old_hash = user.password_hash
        user.set_password("new_password")
        assert user.password_hash != old_hash
        assert user.verify_password("new_password") is True


class TestRoleManagement:
    """Tests for user roles."""

    def test_default_role_is_user(self):
        user = User("john", password="password")
        assert user.role == "user"

    def test_is_admin_method(self):
        admin = User("admin", password="password", role="admin")
        assert admin.is_admin() is True
        regular = User("john", password="password")
        assert regular.is_admin() is False

    def test_is_guest_method(self):
        guest = User("guest", password="guest123", role="guest")
        assert guest.is_guest() is True
        regular = User("john", password="password")
        assert regular.is_guest() is False


class TestUserSerialization:
    """Tests for user serialization."""

    def test_to_dict(self):
        user = User("john", password="password", email="john@email.com")
        data = user.to_dict()
        assert data["username"] == "john"
        assert data["role"] == "user"
        assert data["is_active"] is True

    def test_from_dict(self):
        data = {
            "user_id": "123",
            "username": "john",
            "email": "john@email.com",
            "password_hash": "hash",
            "role": "user",
            "is_active": True,
            "created_at": "2024-01-15T10:00:00",
        }
        user = User.from_dict(data)
        assert user.user_id == "123"
        assert user.username == "john"
        assert user.role == "user"
