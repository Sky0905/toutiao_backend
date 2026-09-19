from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import favorite as favorite_crud
from app.dependencies import db_session
from app.schemas.favorite import FavoriteCreate, FavoriteRead
from app.schemas.common import ApiResponse
from app.utils.responses import success

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.post(
    "",
    response_model=ApiResponse[FavoriteRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_favorite(payload: FavoriteCreate, db: AsyncSession = Depends(db_session)):
    # 重复收藏或关联的用户/新闻不存在时，统一返回冲突错误。
    try:
        favorite = await favorite_crud.create_favorite(db, payload)
        return success(data=FavoriteRead.model_validate(favorite), message="收藏成功")
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="收藏已存在或关联数据不存在")


@router.get("/{user_id}", response_model=ApiResponse[list[FavoriteRead]])
async def read_favorites(user_id: int, db: AsyncSession = Depends(db_session)):
    # 路径参数 user_id 必须是整数。
    favorites = await favorite_crud.list_favorites(db, user_id)
    return success(
        data=[FavoriteRead.model_validate(item) for item in favorites],
        message="查询收藏成功",
    )


@router.delete("/{user_id}/{news_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(user_id: int, news_id: int, db: AsyncSession = Depends(db_session)):
    # DELETE 接口成功时返回 204，不携带响应正文。
    # user_id 和 news_id 都会先由 FastAPI 转换为整数。
    if not await favorite_crud.delete_favorite(db, user_id, news_id):
        raise HTTPException(status_code=404, detail="Favorite not found")
