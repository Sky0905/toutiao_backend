from collections.abc import AsyncGenerator

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.utils.security import decode_access_token


# 从 Authorization: Bearer <token> 请求头中提取 JWT。
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def db_session() -> AsyncGenerator[AsyncSession, None]:
    # 路由通过 Depends 注入异步数据库会话，避免手动管理连接。
    async for db in get_db():
        yield db


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(db_session),
) -> User:
    """校验 JWT，并查询当前登录用户。"""
    try:
        user_id = decode_access_token(token)
    except (ValueError, TypeError, jwt.PyJWTError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
