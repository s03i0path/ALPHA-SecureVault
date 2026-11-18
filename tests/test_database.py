from alpha_vault.database import VaultDatabase
from alpha_vault.crypto import make_salt, password_hash

def test_create_and_get_user(tmp_path):
    db = VaultDatabase(str(tmp_path / "test.db"))
    salt = make_salt()
    user_id = db.create_user("alpha", salt, password_hash("long password", salt), make_salt())
    user = db.get_user("alpha")
    assert user["id"] == user_id
    assert user["username"] == "alpha"

def test_duplicate_username_rejected(tmp_path):
    db = VaultDatabase(str(tmp_path / "test.db"))
    salt = make_salt()
    db.create_user("alpha", salt, password_hash("long password", salt), make_salt())
    try:
        db.create_user("alpha", salt, password_hash("long password", salt), make_salt())
        assert False, "duplicate should fail"
    except Exception:
        assert True

def test_entry_crud_is_user_scoped(tmp_path):
    db = VaultDatabase(str(tmp_path / "test.db"))
    salt = make_salt()
    uid = db.create_user("alpha", salt, password_hash("long password", salt), make_salt())
    entry_id = db.add_entry(uid, b"encrypted")
    assert len(db.list_entries(uid)) == 1
    assert not db.delete_entry(entry_id, uid + 100)
    assert db.update_entry(entry_id, uid, b"updated")
    assert db.delete_entry(entry_id, uid)
    assert db.list_entries(uid) == []
