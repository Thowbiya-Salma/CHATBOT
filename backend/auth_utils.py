# ============================================================
# AUTH UTILITIES - DR. URCW AI
# ============================================================

import bcrypt


# ============================================================
# HASH PASSWORD
# ============================================================

def hash_password(password: str) -> str:
    """
    Hashes a plain text password using bcrypt.
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


# ============================================================
# VERIFY PASSWORD
# ============================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a stored hash.
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)