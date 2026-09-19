from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import history as history_crud
from app.dependencies import db_session
from app.schemas.history import HistoryCreate, HistoryRead
from app.schemas.common import ApiResponse
from app.utils.responses import success

router = APIRouter(prefix="/history", tags=["history"])


@router.post(
    "",
    response_model=ApiResponse[HistoryRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_history(payload: HistoryCreate, db: AsyncSession = Depends(db_session)):
    # 记录一次用户阅读新闻的行为。
    history = await history_crud.create_history(db, payload)
    return success(data=HistoryRead.model_validate(history), message="记录浏览历史成功")


@router.get("/{user_id}", response_model=ApiResponse[list[HistoryRead]])
async def read_history(user_id: int, db: AsyncSession = Depends(db_session)):
    # 路径参数 user_id 必须是整数。
    histories = await history_crud.list_histories(db, user_id)
    return success(
        data=[HistoryRead.model_validate(item) for item in histories],
        message="查询浏览历史成功",
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def clear_history(user_id: int, db: AsyncSession = Depends(db_session)):
    # 没有可清除的记录时返回 404，方便前端识别状态。
    # 路径参数 user_id 必须是整数。
    deleted = await history_crud.clear_histories(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="History not found")
