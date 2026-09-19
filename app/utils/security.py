from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.config import settings


def hash_password(password: str) -> str:
    """使用 bcrypt 对密码做不可逆哈希，数据库不保存明文密码。"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, stored_password: str) -> bool:
    """校验密码，并兼容项目早期生成的 PBKDF2 密码。"""
    if stored_password.startswith("$2"):
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"),
                stored_password.encode("utf-8"),
            )
        except ValueError:
            return False

    # 兼容旧版本的 salt$sha256_digest 格式，便于已有用户平滑升级。
    try:
        salt_hex, digest_hex = stored_password.split("$", maxsplit=1)
        salt = bytes.fromhex(salt_hex)
    except (ValueError, TypeError):
        return False

    import hashlib

    calculated_digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 120_000)
    return calculated_digest.hex() == digest_hex


def create_access_token(user_id: int) -> str:
    """生成包含用户 ID 和过期时间的 JWT。"""
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {"sub": str(user_id), "exp": expires_at}
    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> int:
    """解析并校验 JWT，返回其中的用户 ID。"""
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )
    subject = payload.get("sub")
    if not subject:
        raise ValueError("Token subject is missing")
    return int(subject)
