import pytest
from alpha_vault.crypto import make_salt, password_hash, verify_password, derive_fernet, encrypt_text, decrypt_text

def test_hash_verifies():
    salt = make_salt()
    digest = password_hash("correct horse battery staple", salt)
    assert verify_password("correct horse battery staple", salt, digest)

def test_wrong_password_fails():
    salt = make_salt()
    digest = password_hash("correct horse battery staple", salt)
    assert not verify_password("wrong password", salt, digest)

def test_fernet_round_trip():
    f = derive_fernet("long master password", make_salt())
    token = encrypt_text(f, "secret text")
    assert decrypt_text(f, token) == "secret text"

def test_different_salt_cannot_decrypt_ciphertext():
    password = "long master password"
    f1 = derive_fernet(password, make_salt())
    f2 = derive_fernet(password, make_salt())
    token = encrypt_text(f1, "secret")
    with pytest.raises(ValueError):
        decrypt_text(f2, token)

def test_tampered_ciphertext_rejected():
    f = derive_fernet("long master password", make_salt())
    token = encrypt_text(f, "secret")
    damaged = token[:-2] + (b"AA" if token[-2:] != b"AA" else b"BB")
    with pytest.raises(ValueError):
        decrypt_text(f, damaged)
