from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.history import History
from app.schemas.history import HistoryCreate


async def create_history(db: AsyncSession, payload: HistoryCreate) -> History:
    # 每次阅读都新增一条记录，用于保留完整浏览轨迹。
    history = History(**payload.model_dump())
    db.add(history)
    await db.commit()
    await db.refresh(history)
    return history


async def list_histories(db: AsyncSession, user_id: int, limit: int = 50) -> list[History]:
    query = (
        select(History)
        .where(History.user_id == user_id)
        .order_by(History.viewed_at.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    return list(result.scalars().all())


async def clear_histories(db: AsyncSession, user_id: int) -> int:
    # 清空用户的全部历史记录，返回删除的记录数。
    result = await db.execute(delete(History).where(History.user_id == user_id))
    await db.commit()
    return result.rowcount
