import base64
import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from app.core.config import settings

try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError:
    Fernet = None
    InvalidToken = Exception

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
    expires_delta: timedelta | None = None,
) -> str:
    """Create a new signed JWT access token."""
    to_encode = {"sub": subject, "role": role, "type": "access"}
    if business_id:
        to_encode["business_id"] = business_id
    if extra_claims:
        to_encode.update(extra_claims)

    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta is not None else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(subject: str, extra_claims: dict | None = None) -> str:
    """Create a new signed JWT refresh token."""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"sub": subject, "type": "refresh", "exp": expire}
    if extra_claims:
        to_encode.update(extra_claims)
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise ValueError("Invalid token")


def _get_fernet():
    if Fernet is None:
        return None
    key_bytes = base64.urlsafe_b64encode(hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest())
    return Fernet(key_bytes)


def encrypt_secret(plaintext: str) -> str:
    """Encrypt a merchant credential at rest using Fernet (AES-128-CBC + HMAC)."""
    clean = (plaintext or "").strip()
    if not clean:
        return ""
    if clean.startswith("enc:"):
        return clean
    f = _get_fernet()
    if f is None:
        return clean
    return "enc:" + f.encrypt(clean.encode("utf-8")).decode("utf-8")


def decrypt_secret(ciphertext: str) -> str:
    """Decrypt an at-rest encrypted credential (transparently handles legacy plaintext)."""
    val = (ciphertext or "").strip()
    if not val:
        return ""
    if not val.startswith("enc:"):
        return val
    f = _get_fernet()
    if f is None:
        return val
    try:
        return f.decrypt(val[4:].encode("utf-8")).decode("utf-8")
    except InvalidToken:
        return ""


def mask_secret(val: str) -> str:
    """Return a masked display string like ••••1234 without exposing the secret."""
    plain = decrypt_secret(val)
    if not plain:
        return ""
    return f"••••{plain[-4:]}" if len(plain) >= 4 else "••••"


def decrypt_credentials_dict(creds: dict | None) -> dict:
    """Decrypt all `enc:` values in a PaymentGatewayConfig.merchant_credentials dict."""
    if not isinstance(creds, dict):
        return {}
    return {k: (decrypt_secret(v) if isinstance(v, str) else v) for k, v in creds.items()}
