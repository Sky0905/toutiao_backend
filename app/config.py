from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):     #BaseSettings 会自动去环境变量和 .env 文件里找同名字段，找到就覆盖默认值
    # 应用基础配置，支持通过项目根目录下的 .env 文件覆盖默认值。
    app_name: str
    app_env: str
    debug: bool = True
    # 项目固定使用 MySQL 异步连接，驱动必须是 aiomysql。
    database_url: str
    api_v1_prefix: str
    # JWT 签名密钥必须放在 .env 中，不能使用示例值部署。
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    # Redis 缓存配置，默认连接本机 6379 端口的第 0 个数据库。
    redis_url: str = "redis://127.0.0.1:6379/0"
    redis_cache_ttl_seconds: int = 300

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    # 缓存配置对象，避免每次导入或请求时重复读取环境变量。
    return Settings()


settings = get_settings()
