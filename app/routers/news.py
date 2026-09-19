from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import news as news_crud
from app.dependencies import db_session
from app.schemas.news import NewsCreate, NewsRead
from app.utils.pagination import Page, PageSize, offset
from app.schemas.common import ApiResponse
from app.utils.responses import success

router = APIRouter(prefix="/news", tags=["news"])


@router.post(
    "",
    response_model=ApiResponse[NewsRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_news(payload: NewsCreate, db: AsyncSession = Depends(db_session)):
    # payload 会先经过 NewsCreate 的非空、长度和日期格式校验。
    news = await news_crud.create_news(db, payload)
    return success(data=NewsRead.model_validate(news), message="创建新闻成功")


@router.get("", response_model=ApiResponse[list[NewsRead]])
async def read_news(
    category: str | None = None,
    page: Page = 1,
    page_size: PageSize = 20,
    db: AsyncSession = Depends(db_session),  #自动创建一个新的数据库会话
):
    # category 可选，不传时返回全部分类的新闻。
    news_list = await news_crud.list_news(
        db,
        skip=offset(page, page_size),
        limit=page_size,
        category=category,
    )
    return success(
        data=[NewsRead.model_validate(item) for item in news_list],
        message="查询新闻成功",
    )


@router.get("/{news_id}", response_model=ApiResponse[NewsRead])
async def read_news_item(news_id: int, db: AsyncSession = Depends(db_session)):
    # 路径参数 news_id 必须能够转换为整数。
    news = await news_crud.get_news(db, news_id)
    if news is None:
        raise HTTPException(status_code=404, detail="News not found")
    return success(data=NewsRead.model_validate(news), message="查询新闻成功")
