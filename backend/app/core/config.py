from pydantic_settings import BaseSettings, SettingsConfigDict
import base64


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    JWT_PRIVATE_KEY_B64: str
    JWT_PUBLIC_KEY_B64: str
    JWT_KEY_ID: str | None = None

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_ROTATION: bool = True

    # Redis
    REDIS_URL: str

    # Tenant Defaults
    TENANT_DEFAULT_TIMEZONE: str = "UTC"

    @property
    def JWT_PRIVATE_KEY(self) -> str:
        return base64.b64decode(self.JWT_PRIVATE_KEY_B64).decode()

    @property
    def JWT_PUBLIC_KEY(self) -> str:
        return base64.b64decode(self.JWT_PUBLIC_KEY_B64).decode()

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
