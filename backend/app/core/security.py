import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from app.core.config import settings

try:
    import bcrypt as _bcrypt
except ImportError:
    _bcrypt = None


def _prepare_password_bytes(password: str) -> bytes:
    raw = password.encode("utf-8")
    if len(raw) > 72:
        return hashlib.sha256(raw).hexdigest().encode("utf-8")
    return raw


def hash_password(password: str) -> str:
    """Hash a password using native bcrypt (compatible with Python 3.12+ and bcrypt 4.x/5.x)."""
    pw_bytes = _prepare_password_bytes(password)
    if _bcrypt is not None:
        return _bcrypt.hashpw(pw_bytes, _bcrypt.gensalt()).decode("utf-8")
    digest = hashlib.pbkdf2_hmac("sha256", pw_bytes, settings.SECRET_KEY.encode("utf-8"), 100_000)
    return f"pbkdf2_sha256${digest.hex()}"


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain password against a stored bcrypt or pbkdf2 hash."""
    if not hashed:
        return False
    pw_bytes = _prepare_password_bytes(plain)
    if hashed.startswith("pbkdf2_sha256$"):
        expected = hashed.split("$", 1)[1]
        actual = hashlib.pbkdf2_hmac("sha256", pw_bytes, settings.SECRET_KEY.encode("utf-8"), 100_000).hex()
        return hmac.compare_digest(expected, actual)
    if _bcrypt is not None:
        try:
            return _bcrypt.checkpw(pw_bytes, hashed.encode("utf-8"))
        except ValueError:
            return False
    return False


def create_access_token(
    subject: str,
    role: str,
    business_id: str | None = None,
    extra_claims: dict | None = None,
) -> str:
    """Create a new signed JWT access token."""
    to_encode = {"sub": subject, "role": role, "type": "access"}
    if business_id:
        to_encode["business_id"] = business_id
    if extra_claims:
        to_encode.update(extra_claims)

    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(subject: str) -> str:
    """Create a new signed JWT refresh token."""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"sub": subject, "type": "refresh", "exp": expire}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise ValueError("Invalid token")
