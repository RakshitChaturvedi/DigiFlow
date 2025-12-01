from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import bcrypt

argon2_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=1,
    hash_len=32,
    salt_len=16,
)


def hash_password(password: str) -> str:
    # hash using argon2, if not available, use bcrypt
    try:
        return argon2_hasher.hash(password)
    except Exception:
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
        return hashed.decode()


def verify_password(password: str, hashed: str) -> bool:
    if hashed.startswith("$argon2"):
        try:
            argon2_hasher.verify(hashed, password)
            return True
        except VerifyMismatchError:
            return False
        except Exception:
            return False

    if hashed.startswith("$2b$") or hashed.startswith("$2a$"):
        return bcrypt.checkpw(password.encode(), hashed.encode())

    return False
