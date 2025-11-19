from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.core.config import settings

# Use pbkdf2_sha256 instead of bcrypt to avoid compatibility issues
# and the 72-byte password limit
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a refresh token with 7 days expiry"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_otp_verification_token(user_id: str, email: str) -> str:
    """Create a token for OTP verification (10 minutes expiry)"""
    expire = datetime.utcnow() + timedelta(minutes=10)
    to_encode = {"sub": user_id, "email": email, "exp": expire, "type": "otp_verify"}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_otp_verification_token(token: str) -> dict | None:
    """Verify OTP verification token and return payload if valid"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != "otp_verify":
            return None
        return payload
    except JWTError:
        return None


def create_reset_token(user_id: str, email: str) -> str:
    """Create a short-lived reset token (5 minutes)"""
    expire = datetime.utcnow() + timedelta(minutes=5)
    to_encode = {"sub": user_id, "email": email, "exp": expire, "type": "reset"}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_reset_token(token: str) -> dict | None:
    """Verify reset token and return payload if valid"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != "reset":
            return None
        return payload
    except JWTError:
        return None


def verify_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
