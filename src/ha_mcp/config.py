from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ha_url: str
    ha_token: str
    mcp_host: str = "0.0.0.0"
    mcp_port: int = 8080

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
