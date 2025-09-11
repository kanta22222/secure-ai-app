import os
import uuid
from cryptography.fernet import Fernet

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
FERNET_PATH = os.path.join(DATA_DIR, "fernet.key")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(STORAGE_DIR, exist_ok=True)

def get_or_create_fernet():
    if os.path.exists(FERNET_PATH):
        key = open(FERNET_PATH, "rb").read()
    else:
        key = Fernet.generate_key()
        with open(FERNET_PATH, "wb") as f:
            f.write(key)
    return Fernet(key)

def save_encrypted_file(owner: str, filename: str, raw_bytes: bytes):
    """
    Saves encrypted file bytes into storage and returns storage name.
    Caller should persist a FileRecord with storage_name.
    """
    fernet = get_or_create_fernet()
    token = fernet.encrypt(raw_bytes)
    storage_name = f"{uuid.uuid4().hex}.enc"
    path = os.path.join(STORAGE_DIR, storage_name)
    with open(path, "wb") as f:
        f.write(token)
    return storage_name

def load_decrypted_file(storage_name: str):
    fernet = get_or_create_fernet()
    path = os.path.join(STORAGE_DIR, storage_name)
    if not os.path.exists(path):
        raise FileNotFoundError(storage_name)
    token = open(path, "rb").read()
    return fernet.decrypt(token)
