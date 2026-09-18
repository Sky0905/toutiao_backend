from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.news import News
from app.schemas.news import NewsCreate


async def create_news(db: AsyncSession, payload: NewsCreate) -> News:
    # 将 Pydantic 请求对象转换为 SQLAlchemy 新闻模型并持久化。
    news = News(**payload.model_dump())
    db.add(news)
    await db.commit()
    await db.refresh(news)
    return news


async def get_news(db: AsyncSession, news_id: int) -> News | None:
    return await db.get(News, news_id)


async def list_news(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    category: str | None = None,
) -> list[News]:
    # 默认按创建时间倒序，保证最新新闻优先返回。
    query = select(News).order_by(News.created_at.desc()).offset(skip).limit(limit)
    if category:
        query = query.where(News.category == category)
    result = await db.execute(query)
    return list(result.scalars().all())
