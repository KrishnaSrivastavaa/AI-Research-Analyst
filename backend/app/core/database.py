from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.configs import settings
from sqlalchemy import text
import asyncio

from sqlalchemy.engine import make_url




engine = create_async_engine(settings.database_url, echo=True)

SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()



# async def test_connection():
#     async with engine.connect() as conn:
#         result = await conn.execute(text("SELECT 1"))
#         print(result.scalar())


# if __name__ == "__main__":
#     asyncio.run(test_connection())