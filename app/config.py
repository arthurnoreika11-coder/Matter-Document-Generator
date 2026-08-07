from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    resend_api_key: str = ""
    from_email: str = ""
    database_url: str = "sqlite:///./audit.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()