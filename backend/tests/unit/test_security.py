from app.core.security import hash_password, verify_password


def test_password_hash_and_verify():
    password = "StrongPass123214523!"

    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("RandomShi", hashed) is False


def test_hash_consistency_without_determinism():
    password = "blablabla12321"

    h1 = hash_password(password)
    h2 = hash_password(password)

    assert h1 != h2
    assert verify_password(password, h1)
    assert verify_password(password, h2)
