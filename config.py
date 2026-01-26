import os
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self) -> None:
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///borrowed_books.db")
        self.SECRET_KEY = os.getenv("SECRET_KEY", "local-dev-secret-key")
        self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
        self.DOCS_USERNAME = os.getenv("DOCS_USERNAME", "admin")
        self.DOCS_PASSWORD = os.getenv("DOCS_PASSWORD", "admin")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
