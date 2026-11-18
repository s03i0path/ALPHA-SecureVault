import base64
import hashlib
import hmac
import os
from cryptography.fernet import Fernet, InvalidToken

ITERATIONS = 600_000

def make_salt() -> bytes:
    return os.urandom(16)

def password_hash(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)

def derive_fernet(password: str, salt: bytes) -> Fernet:
    raw_key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS, dklen=32)
    return Fernet(base64.urlsafe_b64encode(raw_key))

def encrypt_text(fernet: Fernet, plaintext: str) -> bytes:
    return fernet.encrypt(plaintext.encode("utf-8"))

def decrypt_text(fernet: Fernet, token: bytes) -> str:
    try:
        return fernet.decrypt(token).decode("utf-8")
    except InvalidToken as exc:
        raise ValueError("رمزگشایی ناموفق بود؛ رمز اصلی اشتباه است یا داده دستکاری شده است.") from exc

def verify_password(password: str, salt: bytes, expected: bytes) -> bool:
    return hmac.compare_digest(password_hash(password, salt), expected)
