import hashlib
import secrets


def hash_password(password: str) -> str:
    # 每个密码使用随机盐，降低相同密码产生相同哈希的风险。
    salt = secrets.token_bytes(16)
    # PBKDF2 通过重复计算增加破解成本。
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 120_000)
    return f"{salt.hex()}${digest.hex()}"
