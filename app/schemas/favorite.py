from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FavoriteCreate(BaseModel):
    """创建收藏时的请求参数校验模型。"""

    # 这两个字段必须是整数，用于关联用户和新闻。
    user_id: int
    news_id: int


class FavoriteRead(FavoriteCreate):
    """收藏接口的响应参数校验模型。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime | None = None
