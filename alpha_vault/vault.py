import json
from .crypto import encrypt_text, decrypt_text

class VaultService:
    def __init__(self, database, user_id, fernet):
        self.db = database
        self.user_id = user_id
        self.fernet = fernet

    def add(self, title, username, password, website="", notes=""):
        payload = {
            "title": title.strip(),
            "username": username.strip(),
            "password": password,
            "website": website.strip(),
            "notes": notes.strip()
        }
        token = encrypt_text(self.fernet, json.dumps(payload, ensure_ascii=False))
        return self.db.add_entry(self.user_id, token)

    def all(self):
        results = []
        for row in self.db.list_entries(self.user_id):
            payload = json.loads(decrypt_text(self.fernet, row["encrypted_payload"]))
            payload["id"] = row["id"]
            results.append(payload)
        return results

    def update(self, entry_id, title, username, password, website="", notes=""):
        payload = {
            "title": title.strip(),
            "username": username.strip(),
            "password": password,
            "website": website.strip(),
            "notes": notes.strip()
        }
        token = encrypt_text(self.fernet, json.dumps(payload, ensure_ascii=False))
        return self.db.update_entry(entry_id, self.user_id, token)

    def delete(self, entry_id):
        return self.db.delete_entry(entry_id, self.user_id)
