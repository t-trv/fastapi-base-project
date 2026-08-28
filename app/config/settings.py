import os
from dotenv import load_dotenv

# Load .env first, then override with .env.local if present
load_dotenv(".env")
load_dotenv(".env.local", override=True)


class Settings:
    # App Information
    APP_NAME: str = "Boilerplate API"
    APP_VERSION: str = "1.0.0"
    APP_PORT: int = int(os.getenv("APP_PORT", "5100"))

    # Database Configuration
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "bosky_db")

    # JWT Configuration
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your_jwt_secret_key_here")
    JWT_ACCESS_EXPIRES_IN: str = os.getenv("JWT_ACCESS_EXPIRES_IN", "15m")
    JWT_REFRESH_EXPIRES_IN: str = os.getenv("JWT_REFRESH_EXPIRES_IN", "7d")

    # Telegram Configuration
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "your_telegram_bot_token_here")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "your_telegram_chat_id_here")

    @property
    def database_url(self) -> str:
        # Use postgresql+asyncpg for Asynchronous SQLAlchemy connection
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
