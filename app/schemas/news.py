from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NewsCreate(BaseModel):
    """创建新闻时的请求参数校验模型。"""

    # 标题不能为空，长度不能超过 200 个字符。
    title: str = Field(min_length=1, max_length=200)
    # 摘要是可选字段；如果填写，长度不能超过 500 个字符。
    summary: str | None = Field(default=None, max_length=500)
    # 正文不能为空。
    content: str = Field(min_length=1)
    # 以下字段允许不填写，但填写后会限制最大长度。
    source: str | None = Field(default=None, max_length=100)
    category: str | None = Field(default=None, max_length=50)
    # Pydantic 会尝试把传入的日期字符串转换为 datetime。
    published_at: datetime | None = None


class NewsRead(NewsCreate):
    """新闻接口的响应参数校验模型。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime | None = None
