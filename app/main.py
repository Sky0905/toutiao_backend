from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi import Depends
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import create_tables, engine
from app.dependencies import db_session
from app.routers import auth, favorite, history, news, users

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


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    # 用于部署检查和确认服务是否正常运行。
    return {"status": "ok", "environment": settings.app_env}


@app.get("/health/db", tags=["system"])
async def database_health_check(db: AsyncSession = Depends(db_session)):
    """执行真实数据库查询，确认 MySQL 连接和会话都可用。"""
    try:
        await db.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "database": "mysql",
            "message": "Database connection is healthy",
        }
    except Exception as exc:
        # 不把数据库账号、密码或底层连接细节返回给客户端。
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "database": "mysql",
                "message": "Database connection failed",
                "error_type": type(exc).__name__,
            },
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
