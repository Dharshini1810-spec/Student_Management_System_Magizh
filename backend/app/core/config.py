import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    DATABASE_URL: str = Field(..., env='DATABASE_URL')
    JWT_SECRET_KEY: str = Field(..., env='JWT_SECRET_KEY')
    JWT_ALGORITHM: str = Field(default='HS256', env='JWT_ALGORITHM')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, env='ACCESS_TOKEN_EXPIRE_MINUTES')
    PROJECT_NAME: str = 'Student Management System'
    API_V1_STR: str = '/api/v1'

    model_config = SettingsConfigDict(
        env_file=os.getenv('ENV_PATH', '.env'),
        env_file_encoding='utf-8',
        extra='ignore'  # Ignore extra fields from .env
    )

settings = Settings()
