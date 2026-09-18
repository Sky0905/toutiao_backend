from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db


async def db_session() -> AsyncGenerator[AsyncSession, None]:
    # 路由通过 Depends 注入异步数据库会话，避免手动管理连接。
    async for db in get_db():
        yield db
