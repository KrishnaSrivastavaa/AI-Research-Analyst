from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.configs import settings
from sqlalchemy import text
import asyncio

from sqlalchemy.engine import make_url




engine = create_async_engine(settings.database_url, echo=False)

SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()

