"""Get-or-create the per-device household and load it with its relations.

v0 has no login: each device owns exactly one household, created lazily on the
first request that needs it.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.household import Household


async def get_or_create_household(db: AsyncSession, device_uuid: str) -> Household:
    result = await db.execute(
        select(Household)
        .where(Household.device_uuid == device_uuid)
        .options(
            selectinload(Household.members),
            selectinload(Household.goal),
            selectinload(Household.schedule),
        )
    )
    household = result.scalars().first()
    if household is not None:
        return household

    household = Household(device_uuid=device_uuid, dietary_preferences={}, cuisines=[])
    db.add(household)
    await db.flush()
    # newly created: relations are empty collections / None
    await db.refresh(household, attribute_names=["members", "goal", "schedule"])
    return household
