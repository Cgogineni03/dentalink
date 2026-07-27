# DentaLink Cryptographic & Security Helpers
import base64
import hashlib
import hmac
import json
import secrets
import sys

ACTIVE_SESSION_CMK = None


def get_active_session_cmk():
    """Gets current active session master key, resolving facade module state."""
    global ACTIVE_SESSION_CMK
    if 'database' in sys.modules and hasattr(sys.modules['database'], 'ACTIVE_SESSION_CMK'):
        mod_cmk = getattr(sys.modules['database'], 'ACTIVE_SESSION_CMK')
        if mod_cmk is not None:
            return mod_cmk
    return ACTIVE_SESSION_CMK


def set_active_session_cmk(key_bytes):
    """Sets active session master key across module contexts."""
    global ACTIVE_SESSION_CMK
    ACTIVE_SESSION_CMK = key_bytes
    if 'database' in sys.modules:
        setattr(sys.modules['database'], 'ACTIVE_SESSION_CMK', key_bytes)


def derive_key(secret_str: str, salt_bytes: bytes) -> bytes:
    """Derives a 256-bit key using PBKDF2 HMAC-SHA256."""
    return hashlib.pbkdf2_hmac('sha256', secret_str.encode('utf-8'), salt_bytes, 100000)


def xor_crypt(data: bytes, key: bytes) -> bytes:
    """Stream cipher payload transformation using SHA256 key keystream."""
    out = bytearray()
    for i, b in enumerate(data):
        ks = hashlib.sha256(key + i.to_bytes(4, 'big')).digest()[0]
        out.append(b ^ ks)
    return bytes(out)


def encrypt_payload(data_obj, key: bytes = None) -> str:
    """Encrypts a Python dictionary or string payload into a Base64 ciphertext string."""
    k = key or get_active_session_cmk() or b"DENTA_LINK_MASTER_CMK_SESSION_256"
    raw_bytes = json.dumps(data_obj).encode('utf-8')
    ciphertext = xor_crypt(raw_bytes, k)
    return base64.b64encode(ciphertext).decode('utf-8')


def decrypt_payload(cipher_str: str, key: bytes = None):
    """Decrypts a Base64 ciphertext string into Python object."""
    if not cipher_str:
        return {}
    k = key or get_active_session_cmk() or b"DENTA_LINK_MASTER_CMK_SESSION_256"
    try:
        raw_bytes = base64.b64decode(cipher_str.encode('utf-8'))
        plain_bytes = xor_crypt(raw_bytes, k)
        return json.loads(plain_bytes.decode('utf-8'))
    except Exception:
        return {}


def compute_hmac(data_str: str, key: bytes = None) -> str:
    """Computes HMAC-SHA256 signature for tamper verification."""
    k = key or get_active_session_cmk() or b"DENTA_LINK_MASTER_CMK_SESSION_256"
    return hmac.new(k, data_str.encode('utf-8'), hashlib.sha256).hexdigest()


def generate_universal_recovery_key() -> str:
    """Generates a 16-character formatted Universal Emergency Recovery Key (XXXX-XXXX-XXXX-XXXX)."""
    chars = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
    p1 = "".join(secrets.choice(chars) for _ in range(4))
    p2 = "".join(secrets.choice(chars) for _ in range(4))
    p3 = "".join(secrets.choice(chars) for _ in range(4))
    p4 = "".join(secrets.choice(chars) for _ in range(4))
    return f"{p1}-{p2}-{p3}-{p4}"


def normalize_recovery_key(key: str) -> str:
    """Normalizes recovery key by stripping hyphens and spaces."""
    return (key or "").replace("-", "").replace(" ", "").strip().upper()


def normalize_answer(ans: str) -> str:
    """Normalizes security answers for case-insensitive matching."""
    return (ans or "").strip().lower()


def hash_answer(ans: str, salt: bytes) -> str:
    """Computes case-insensitive answer hash."""
    norm = normalize_answer(ans)
    return hashlib.pbkdf2_hmac('sha256', norm.encode('utf-8'), salt, 100000).hex()
