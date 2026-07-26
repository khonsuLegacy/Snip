import random
import string

ALPHABET = string.ascii_letters + string.digits  # 62 characters


def generate_short_code(length: int = 6) -> str:
    """Generate a random base62 short code, e.g. 'aZ3kP9'."""
    return "".join(random.choices(ALPHABET, k=length))


def encode_base62(num: int) -> str:
    """Deterministically turn a numeric primary key into a base62 string.
    Useful as a fallback/alternative to random codes (guarantees no collisions)."""
    if num == 0:
        return ALPHABET[0]
    digits = []
    base = len(ALPHABET)
    while num:
        num, rem = divmod(num, base)
        digits.append(ALPHABET[rem])
    return "".join(reversed(digits))
