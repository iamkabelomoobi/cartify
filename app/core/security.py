from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings


class AuthService:
    def __init__(
        self,
        secret_key: str | None = None,
        algorithm: str | None = None,
        access_token_expire_minutes: int | None = None,
    ) -> None:
        self.secret_key = secret_key or settings.SECRET_KEY
        self.algorithm = algorithm or settings.ALGORITHM
        self.access_token_expire_minutes = (
            access_token_expire_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

        self.pwd_context = CryptContext(
            schemes=["pbkdf2_sha256"],
            deprecated="auto",
        )

    def hash_password(self, password: str) -> str:
        """Hash a password for storage (must match verify_password)."""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a stored hash."""
        return self.pwd_context.verify(plain_password, hashed_password)

    def _encode(self, data: dict[str, Any]) -> str:
        return jwt.encode(data, self.secret_key, algorithm=self.algorithm)

    def _decode(self, token: str) -> dict[str, Any] | None:
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except JWTError:
            return None

    def create_access_token(
        self, data: dict[str, Any], expires_delta: timedelta | None = None
    ) -> str:
        to_encode = data.copy()
        expire = (
            datetime.utcnow() + expires_delta
            if expires_delta is not None
            else datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        )
        to_encode.update({"exp": expire})
        return self._encode(to_encode)

    def create_refresh_token(self, data: dict[str, Any]) -> str:
        """Create a refresh token with 7 days expiry."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"exp": expire, "type": "refresh"})
        return self._encode(to_encode)

    def create_otp_verification_token(self, user_id: str, email: str) -> str:
        """Create a token for OTP verification (10 minutes expiry)."""
        expire = datetime.utcnow() + timedelta(minutes=10)
        to_encode = {
            "sub": user_id,
            "email": email,
            "exp": expire,
            "type": "otp_verify",
        }
        return self._encode(to_encode)

    def verify_otp_verification_token(self, token: str) -> dict[str, Any] | None:
        """Verify OTP verification token and return payload if valid."""
        payload = self._decode(token)
        if not payload or payload.get("type") != "otp_verify":
            return None
        return payload

    def create_reset_token(self, user_id: str, email: str) -> str:
        """Create a short-lived reset token (5 minutes)."""
        expire = datetime.utcnow() + timedelta(minutes=5)
        to_encode = {
            "sub": user_id,
            "email": email,
            "exp": expire,
            "type": "reset",
        }
        return self._encode(to_encode)

    def verify_reset_token(self, token: str) -> dict[str, Any] | None:
        """Verify reset token and return payload if valid."""
        payload = self._decode(token)
        if not payload or payload.get("type") != "reset":
            return None
        return payload

    def verify_token(self, token: str) -> dict[str, Any] | None:
        """Decode any JWT and return payload if valid."""
        return self._decode(token)

    def get_token_expiration(self, token: str) -> datetime:
        """Extract expiration time from JWT token."""
        try:
            payload = self._decode(token)
            if not payload:
                return datetime.now(timezone.utc)

            exp_timestamp = payload.get("exp")
            if exp_timestamp:
                return datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)

            return datetime.now(timezone.utc)
        except Exception:
            return datetime.now(timezone.utc)
