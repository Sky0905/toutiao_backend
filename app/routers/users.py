from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import users as user_crud
from app.dependencies import db_session, get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.utils.pagination import Page, PageSize, offset

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
async def read_my_profile(current_user: User = Depends(get_current_user)):
    """示例受保护接口：只有携带有效 JWT 才能访问。"""
    return current_user


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, db: AsyncSession = Depends(db_session)):
    # 创建用户；用户名或邮箱重复时返回 409。
    # payload 会先经过 UserCreate 的字段校验，校验失败时 FastAPI 返回 422。
    try:
        return await user_crud.create_user(db, payload)
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Username or email already exists") from exc


@router.get("", response_model=list[UserRead])
async def read_users(
    page: Page = 1,
    page_size: PageSize = 20,
    db: AsyncSession = Depends(db_session),
):
    # page 和 page_size 会由 FastAPI 自动校验范围。
    return await user_crud.list_users(db, skip=offset(page, page_size), limit=page_size)


@router.get("/{user_id}", response_model=UserRead)
async def read_user(user_id: int, db: AsyncSession = Depends(db_session)):
    # user_id 会由 FastAPI 转换并校验为整数。
    user = await user_crud.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
