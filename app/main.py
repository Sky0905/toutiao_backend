from contextlib import asynccontextmanager
import logging
from pathlib import Path
from time import perf_counter
from uuid import uuid4

from fastapi import Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
from starlette.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import create_tables, engine
from app.dependencies import db_session
from app.exceptions.handlers import (
    http_exception_handler,
    integrity_exception_handler,
    sqlalchemy_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.routers import auth, favorite, history, news, users
from app.schemas.common import ApiResponse
from app.utils.app_logging import setup_logging
from app.utils.responses import success


setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(_: FastAPI):
    # 应用启动时自动建表，开发阶段无需额外执行初始化脚本。
    await create_tables()
    try:
        yield
    finally:
        # 应用停止时释放异步连接池。
        await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """记录每次请求的请求 ID、状态码和耗时。"""
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    started_at = perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "Request failed: request_id=%s method=%s path=%s",
            request_id,
            request.method,
            request.url.path,
        )
        raise

    duration_ms = (perf_counter() - started_at) * 1000
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "Request completed: request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)


@app.get("/health", response_model=ApiResponse[dict[str, str]], tags=["system"])
def health_check() -> ApiResponse[dict[str, str]]:
    # 用于部署检查和确认服务是否正常运行。
    return success(
        data={"status": "ok", "environment": settings.app_env},
        message="服务运行正常",
    )


@app.get("/health/db", response_model=ApiResponse[dict[str, str]], tags=["system"])
async def database_health_check(
    db: AsyncSession = Depends(db_session),
) -> ApiResponse[dict[str, str]]:
    """执行真实数据库查询，确认 MySQL 连接和会话都可用。"""
    await db.execute(text("SELECT 1"))
    return success(
        data={"status": "ok", "database": "mysql"},
        message="数据库连接正常",
    )


# 按业务模块注册路由，统一挂载在 /api/v1 下。
app.include_router(users.router, prefix=settings.api_v1_prefix)
app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(news.router, prefix=settings.api_v1_prefix)
app.include_router(favorite.router, prefix=settings.api_v1_prefix)
app.include_router(history.router, prefix=settings.api_v1_prefix)

# 将 frontend 目录作为静态网站挂载，启动后直接访问 http://127.0.0.1:8000/。
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
