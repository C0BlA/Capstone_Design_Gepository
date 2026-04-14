from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    server_url: str = "http://localhost:8000"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8001

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
