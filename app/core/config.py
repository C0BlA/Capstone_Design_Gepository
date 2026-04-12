from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Agent Resource Server"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    database_url: str = "mysql+pymysql://root:root@localhost:3306/agent_server"
    heartbeat_timeout_seconds: int = 20

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
