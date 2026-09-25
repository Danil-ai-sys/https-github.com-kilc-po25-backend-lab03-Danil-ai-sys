Name: Sobar Danil 
Group: PO 25-Z 
Date: 25.09.26

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="CHAT_")

    data_file: str = "messages.json"
    secret: str
    max_messages: int = Field(default=100, ge=1, le=1000)

settings = Settings()
