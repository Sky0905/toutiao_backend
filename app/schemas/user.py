from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """创建用户时的请求参数校验模型。"""

    # 用户名长度限制为 2 到 50 个字符。
    username: str = Field(min_length=2, max_length=50)
    # EmailStr 会检查邮箱格式，例如 test@example.com。
    email: EmailStr
    # 密码长度限制为 6 到 128 个字符。
    # bcrypt 最多处理 72 字节，限制长度避免静默截断。
    password: str = Field(min_length=6, max_length=72)


class UserRead(BaseModel):
    """用户接口的响应参数校验模型。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    # 查询数据库后返回数据时，也会再次校验邮箱格式。
    email: EmailStr
    created_at: datetime | None = None
