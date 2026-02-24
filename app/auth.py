from passlib.context import CryptContext

# ================= PASSWORD CONFIG =================

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

# ================= HASH PASSWORD =================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# ================= VERIFY PASSWORD =================

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)
