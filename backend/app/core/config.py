from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    JWT_PRIVATE_KEY: str
    JWT_PUBLIC_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_ROTATION: bool = True

    # Redis
    REDIS_URL: str

    # Tenant Defaults
    TENANT_DEFAULT_TIMEZONE: str = "UTC"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
