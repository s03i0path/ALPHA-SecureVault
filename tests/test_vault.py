from alpha_vault.database import VaultDatabase
from alpha_vault.crypto import make_salt, password_hash, derive_fernet
from alpha_vault.vault import VaultService

def test_vault_round_trip_and_update(tmp_path):
    db = VaultDatabase(str(tmp_path / "test.db"))
    salt = make_salt()
    uid = db.create_user("alpha", salt, password_hash("long password", salt), make_salt())
    vault = VaultService(db, uid, derive_fernet("long password", make_salt()))
    # Vault encryption is independently exercised here; the service stores and retrieves records.
    vault.add("Mail", "alpha@example.com", "secret123", "https://example.com", "personal")
    rows = vault.all()
    assert rows[0]["title"] == "Mail"
    assert rows[0]["password"] == "secret123"
    assert vault.update(rows[0]["id"], "Mail 2", "alpha@example.com", "secret456")
    assert vault.all()[0]["title"] == "Mail 2"

def test_users_cannot_read_each_others_entries(tmp_path):
    db = VaultDatabase(str(tmp_path / "test.db"))
    salt = make_salt()
    uid1 = db.create_user("alpha1", salt, password_hash("long password", salt), make_salt())
    uid2 = db.create_user("alpha2", salt, password_hash("long password", salt), make_salt())
    f = derive_fernet("long password", make_salt())
    v1 = VaultService(db, uid1, f)
    v2 = VaultService(db, uid2, f)
    v1.add("Private", "user", "secret")
    assert v2.all() == []
