"""
config for the whole project, contains .env variables, please note the use of the @lru_cache
in getting instantiating setting, what it does is that stores the value that the class varianbles
in the Settings class are set to on the first read from the .env file so that when other functions
call on get_settings() rather than doing I/O from the .env file, it uses that cached value, so if
you make any update to the .env file, to make it take effect, restart the server.
"""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

# under the hood, dotenv is used
# Order of reading variables: from passing them in through the Settings constructor -> Environment  -> .env file

BASE_DIR = Path(__file__).resolve().parent.parent # get absolute path to .env

class Settings(BaseSettings):
    """
    please note that these are pydantic fields hence expect different behaviour from the regular python datatypes
    because pydantic has type coercion
    """
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        case_sensitive=True
    )

    # ===============================
    # Application
    # ===============================
    PROJECT_NAME: str = "ITeMS-TRD Learning Management System"
    DEBUG: bool = True

    # ===============================
    # Security
    # ===============================
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ===============================
    # Database
    # ===============================
    DATABASE_URL: str="this would not work in prod as long as you set debug properly"
    PROD_DATABASE_URL: str

    # ===============================
    # CORS
    # ===============================
    ALLOWED_ORIGINS: list[str] = []

    # ===============================
    # MIDDLEWARE
    # ===============================
    SESSION_MIDDLEWARE_SECRET_KEY: str


@lru_cache
def get_setting():
    return Settings()


settings = get_setting()
