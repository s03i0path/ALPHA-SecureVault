from .crypto import make_salt, password_hash, verify_password, derive_fernet

class AuthError(Exception):
    pass

class AuthService:
    def __init__(self, database):
        self.db = database

    def register(self, username: str, password: str):
        username = username.strip()
        if len(username) < 3:
            raise AuthError("نام کاربری باید حداقل ۳ کاراکتر باشد.")
        if len(password) < 10:
            raise AuthError("رمز اصلی باید حداقل ۱۰ کاراکتر باشد.")
        p_salt = make_salt()
        v_salt = make_salt()
        digest = password_hash(password, p_salt)
        try:
            user_id = self.db.create_user(username, p_salt, digest, v_salt)
        except Exception as exc:
            if "UNIQUE" in str(exc):
                raise AuthError("این نام کاربری قبلاً ثبت شده است.") from exc
            raise
        return user_id, derive_fernet(password, v_salt)

    def login(self, username: str, password: str):
        user = self.db.get_user(username.strip())
        if not user or not verify_password(password, user["password_salt"], user["password_hash"]):
            raise AuthError("نام کاربری یا رمز اصلی نادرست است.")
        return user["id"], derive_fernet(password, user["vault_salt"])
