from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ha_url: str
    ha_token: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
