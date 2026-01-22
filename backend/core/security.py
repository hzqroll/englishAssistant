"""
Security utilities.

Handles JWT token creation/verification and password hashing.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt


def create_access_token(
    data: Dict[str, Any],
    secret: str,
    algorithm: str = "HS256",
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token.

    Args:
        data: Data to encode in token (e.g., user_id)
        secret: JWT secret key
        algorithm: JWT algorithm
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token

    Example:
        ```python
        from datetime import timedelta
        token = create_access_token(
            data={"sub": "user_id", "type": "access"},
            secret="secret",
            expires_delta=timedelta(minutes=30)
        )
        ```
    """
    # TODO: Implement JWT creation
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret, algorithm=algorithm)

    return encoded_jwt


def verify_token(token: str, secret: str, algorithm: str = "HS256") -> Optional[Dict[str, Any]]:
    """
    Verify and decode JWT token.

    Args:
        token: JWT token to verify
        secret: JWT secret key
        algorithm: JWT algorithm

    Returns:
        Decoded token payload if valid, None otherwise

    Example:
        ```python
        payload = verify_token(token, "secret")
        if payload:
            user_id = payload.get("sub")
        ```
    """
    # TODO: Implement JWT verification
    try:
        payload = jwt.decode(token, secret, algorithms=[algorithm])
        return payload
    except JWTError:
        return None


def hash_password(password: str, rounds: int = 12) -> str:
    """
    Hash password using bcrypt.

    Args:
        password: Plain text password
        rounds: Number of bcrypt rounds

    Returns:
        Hashed password

    Example:
        ```python
        hashed = hash_password("my_password")
        assert hashed != "my_password"
        ```
    """
    # TODO: Implement password hashing
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=rounds)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password

    Returns:
        True if password matches, False otherwise

    Example:
        ```python
        assert verify_password("password", hash_password("password")) == True
        ```
    """
    # TODO: Implement password verification
    try:
        password_bytes = plain_password.encode('utf-8')
        hash_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception:
        return False
