# ALPHA Secure Vault

A local desktop password vault built with Python, CustomTkinter, SQLite and Fernet encryption.

## Features
- Local account registration and login
- Password-based key derivation (PBKDF2-HMAC-SHA256)
- Fernet authenticated encryption for each vault entry
- Add, edit, delete and search saved entries
- Random password generator
- SQLite parameterized queries
- Master password is never stored in plaintext
- Basic automated tests

## Requirements
- Python 3.10+
- Linux, macOS or Windows

## Install on Arch Linux
```bash
sudo pacman -S --needed python python-pip tk
cd ALPHA-SecureVault
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If pip refuses to install packages into the system Python, use the virtual environment commands above. Do not use `sudo pip`.

## Run
```bash
source .venv/bin/activate
python main.py
```

## Run tests
```bash
source .venv/bin/activate
pytest -q
```

## Data location
The SQLite database is created at `~/.alpha_secure_vault/vault.db`. Back it up only while the application is closed, and protect the backup file with your operating-system account permissions.

## Security notes
- The master password is used to derive an encryption key and verify login; it is not saved.
- Each vault entry is encrypted with Fernet (AES-128-CBC + HMAC-SHA256 as provided by Fernet).
- Password verification uses PBKDF2-HMAC-SHA256 with a per-user random salt.
- This is an educational starter project, not a professionally audited password manager. Use a unique master password and do not store credentials whose loss would cause serious harm until the code has been independently reviewed.
- There is no master-password recovery. If it is forgotten, encrypted entries cannot be decrypted.
