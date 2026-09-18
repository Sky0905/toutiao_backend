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
