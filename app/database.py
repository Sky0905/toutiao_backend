from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    """所有数据库模型的基类。"""


# 使用 aiomysql 驱动创建 MySQL 异步引擎。
# pool_pre_ping 检查连接是否有效，pool_recycle 减少 MySQL 长连接断开问题。
engine: AsyncEngine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=10,
    max_overflow=20,
)

# 每个请求从连接池中获取一个独立的异步数据库会话。
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def create_tables() -> None:
    # 导入模型后，SQLAlchemy 才能发现并创建对应的数据表。
    # create_all 只会创建表，不会创建 MySQL 数据库本身。
    from app import models  # noqa: F401

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    # 每个请求独立使用一个异步数据库会话，请求结束后自动关闭。
    async with AsyncSessionLocal() as db:
        try:
            yield db
        except Exception:
            await db.rollback()
            raise
