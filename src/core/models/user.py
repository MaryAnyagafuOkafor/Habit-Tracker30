"""
USER MODEL - Business Logic Layer
=================================

User model with Argon2 password hashing, role management, and serialization.

Key Features:
    - Argon2 password hashing (secure, resistant to GPU cracking)
    - Role-based access (guest, user, admin)
    - Account activation/deactivation
    - Serialization to/from dictionary

Example:
    >>> user = User("john_doe", "john@email.com", "secure_password")
    >>> user.verify_password("secure_password")
    True
    >>> user.is_admin()
    False
"""

import uuid
from datetime import datetime
from typing import Dict, Any

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, InvalidHash

from src.utils.helpers import to_iso

# Initialize Argon2 Password Hasher
ph = PasswordHasher()


class User:
    """
    User Model with Argon2 Password Hashing.

    Handles authentication, role-based access, account status, and serialization.

    Attributes:
        user_id (str): Unique identifier (UUID v4)
        username (str): User's login name
        email (str): User's email address (optional)
        password_hash (str): Argon2 hashed password
        created_at (datetime): Account creation time
        is_active (bool): Account active status
        role (str): User role - 'guest', 'user', or 'admin'
    """

    # ============================================
    # INITIALIZATION
    # ============================================

    def __init__(
        self,
        username: str,
        password: str = None,
        email: str = "",
        password_hash: str = None,
        role: str = "user",
        user_id: str = None,
        is_active: bool = True,
        created_at: datetime = None,
    ):
        """
        Initialize a User.

        Args:
            username: Username (must be unique)
            password: Plain text password (will be hashed)
            email: Email address (optional)
            password_hash: Existing password hash (for loading from DB)
            role: User role ('user', 'admin', or 'guest')
            user_id: UUID for the user (auto-generated if not provided)
            is_active: Whether the account is active
            created_at: Creation timestamp (defaults to now)
        """
        self.username = username
        self.email = email
        self.role = role if role in ["user", "admin", "guest"] else "user"
        self.user_id = user_id or str(uuid.uuid4())
        self.is_active = is_active
        self.created_at = created_at or datetime.now()

        # Set password hash
        if password_hash:
            self.password_hash = password_hash
        elif password:
            self._hash_password(password)
        else:
            self.password_hash = None

    def _hash_password(self, password: str) -> None:
        """Hash a password using Argon2."""
        self.password_hash = ph.hash(password)

    def verify_password(self, password: str) -> bool:
        """Verify a password against the stored hash."""
        if not self.password_hash:
            return False
        try:
            ph.verify(self.password_hash, password)
            return True
        except (VerificationError, InvalidHash):
            return False

    def set_password(self, password: str) -> None:
        """Set a new password."""
        self._hash_password(password)

    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary for database storage."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": to_iso(self.created_at) if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """Create a User from a dictionary."""
        user = cls(
            username=data.get("username", ""),
            email=data.get("email", ""),
            password=None,  # Don't pass password here, we'll set the hash directly
            user_id=data.get("user_id"),
            role=data.get("role", "user"),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at"),
        )
        # ✅ IMPORTANT: Set the password hash directly
        user.password_hash = data.get("password_hash")
        return user

    def deactivate(self) -> None:
        """Deactivate the user account."""
        self.is_active = False

    def activate(self) -> None:
        """Activate the user account."""
        self.is_active = True

    def is_admin(self) -> bool:
        """Check if the user has admin role."""
        return self.role == "admin"

    def is_guest(self) -> bool:
        """Check if the user has guest role."""
        return self.role == "guest"

    def is_user(self) -> bool:
        """Check if the user has regular user role."""
        return self.role == "user"

    def __str__(self) -> str:
        """String representation of the user."""
        return f"User({self.username}, role={self.role})"
