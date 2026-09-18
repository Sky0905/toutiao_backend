from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.favorite import Favorite
from app.schemas.favorite import FavoriteCreate


async def create_favorite(db: AsyncSession, payload: FavoriteCreate) -> Favorite:
    # 用户和新闻的关联关系由收藏表保存。
    favorite = Favorite(**payload.model_dump())
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite


async def list_favorites(db: AsyncSession, user_id: int) -> list[Favorite]:
    query = select(Favorite).where(Favorite.user_id == user_id).order_by(Favorite.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def delete_favorite(db: AsyncSession, user_id: int, news_id: int) -> bool:
    # 删除指定用户对指定新闻的收藏，并返回是否实际删除了记录。
    result = await db.execute(
        delete(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    )
    await db.commit()
    return result.rowcount > 0
