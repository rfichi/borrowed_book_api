import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.engine.url import make_url
from config import get_settings

_logger = logging.getLogger(__name__)
settings = get_settings()

url = make_url(settings.DATABASE_URL)
print(f"Original Database URL driver: {url.drivername}")
if url.drivername.startswith("postgres"):
    url = url.set(drivername="postgresql+asyncpg")
elif url.drivername == "sqlite":
    url = url.set(drivername="sqlite+aiosqlite")

print(f"Final Async Database URL driver: {url.drivername}")

engine = create_async_engine(
    url,
    connect_args={"check_same_thread": False} if "sqlite" in url.drivername else {},
)
AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)
Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
