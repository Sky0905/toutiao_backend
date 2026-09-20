import json
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.redis import delete_by_pattern, get_redis
from app.config import settings
from app.crud import news as news_crud
from app.dependencies import db_session
from app.schemas.common import ApiResponse
from app.schemas.news import NewsCreate, NewsRead
from app.utils.pagination import Page, PageSize, offset
from app.utils.responses import success

router = APIRouter(prefix="/news", tags=["news"])
logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=ApiResponse[NewsRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_news(payload: NewsCreate, db: AsyncSession = Depends(db_session)):
    # payload 会先经过 NewsCreate 的非空、长度和日期格式校验。
    news = await news_crud.create_news(db, payload)       # 1. 先写入 MySQL
    deleted_count = await delete_by_pattern("news:list:*")    # 2. 删除新闻列表缓存
    logger.info("创建新闻后清理新闻列表缓存，deleted_count=%s", deleted_count)
    return success(data=NewsRead.model_validate(news), message="创建新闻成功")


@router.get("", response_model=ApiResponse[list[NewsRead]])
async def read_news(
    category: str | None = None,
    page: Page = 1,
    page_size: PageSize = 20,
    db: AsyncSession = Depends(db_session),  #自动创建一个新的数据库会话
    redis: Redis = Depends(get_redis),  #FastAPI 自动帮你拿到一个 Redis 客户端对象
):
    # category 可选，不传时返回全部分类的新闻。
    cache_key = f"news:list:category={category or 'all'}:page={page}:page_size={page_size}"  #因为不同参数查询结果不同
    cached = await redis.get(cache_key)     #去 Redis 里查这个 key 有没有值。
    if cached:
        logger.info("新闻列表缓存命中，cache_key=%s", cache_key)
        return success(data=json.loads(cached), message="查询新闻成功")

    logger.info("新闻列表缓存未命中，cache_key=%s", cache_key)
    news_list = await news_crud.list_news(       #news_list 里是 SQLAlchemy 模型对象
        db,
        skip=offset(page, page_size),
        limit=page_size,
        category=category,
    )
    data = [                     #这种对象不能直接存 Redis。所以先转成 Pydantic 响应模型：
        NewsRead.model_validate(item).model_dump(mode="json")  #再转成普通字典：.model_dump(mode="json")
        for item in news_list
    ]
    await redis.setex(   #设置一个 key，并且给它过期时间
        cache_key,     #key
        settings.redis_cache_ttl_seconds,   #seconds
        json.dumps(data, ensure_ascii=False),  #value   #把 Python 列表转成 JSON 字符串，存进 Redis。ensure_ascii=False 是为了中文不变成 Unicode 转义
    )
    logger.info(
        "新闻列表写入 Redis 缓存，cache_key=%s ttl=%s count=%s",
        cache_key,
        settings.redis_cache_ttl_seconds,
        len(data),
    )
    return success(
        data=data,
        message="查询新闻成功",
    )


@router.get("/{news_id}", response_model=ApiResponse[NewsRead])
async def read_news_item(news_id: int, db: AsyncSession = Depends(db_session), redis: Redis = Depends(get_redis)):
    # 路径参数 news_id 必须能够转换为整数。
    cache_key= f"news:item:{news_id}"
    cached = await redis.get(cache_key)
    if cached:
        logger.info("新闻缓存命中，cache_key=%s", cache_key)
        return success(data=json.loads(cached), message="查询新闻成功")

    logger.info("新闻列表缓存未命中，cache_key=%s", cache_key)

    news = await news_crud.get_news(db, news_id)
    if news is None:
        raise HTTPException(status_code=404, detail="News not found")

    data = NewsRead.model_validate(news).model_dump(mode="json")

    await redis.setex(   #设置一个 key，并且给它过期时间
        cache_key,     #key
        settings.redis_cache_ttl_seconds,   #seconds
        json.dumps(data, ensure_ascii=False),  #value   #把 Python 列表转成 JSON 字符串，存进 Redis。ensure_ascii=False 是为了中文不变成 Unicode 转义
    )
    logger.info("新闻详情写入 Redis 缓存，cache_key=%s", cache_key)
    return success(data, message="查询新闻成功")
