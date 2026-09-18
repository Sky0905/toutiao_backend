from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.security import hash_password


async def create_user(db: AsyncSession, payload: UserCreate) -> User:
    # 数据库中只保存密码哈希，不保存用户输入的明文密码。
    user = User(
        username=payload.username,
        email=str(payload.email),
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user(db: AsyncSession, user_id: int) -> User | None:
    # 根据主键查询用户，不存在时返回 None。
    return await db.get(User, user_id)


async def list_users(db: AsyncSession, skip: int = 0, limit: int = 20) -> list[User]:
    # CRUD 层只负责数据访问，分页参数由路由层传入。
    result = await db.execute(select(User).offset(skip).limit(limit))
    return list(result.scalars().all())
