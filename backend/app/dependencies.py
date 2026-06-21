from typing import AsyncGenerator

from fastapi import Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def device_uuid(x_device_uuid: str = Header(..., alias="X-Device-UUID")) -> str:
    """The caller's device identity (v0 has no login). Lower-cased for stability."""
    return x_device_uuid.lower()
