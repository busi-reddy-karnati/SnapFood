from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.dependencies import device_uuid, get_db
from app.models.pantry_item import PantryItem
from app.schemas.domain import PantryItemSchema
from app.schemas.requests import PantryItemCreateRequest, PantryItemUpdateRequest
from app.services.household_service import get_or_create_household

router = APIRouter()

DeviceDep = Annotated[str, Depends(device_uuid)]
DbDep = Annotated[AsyncSession, Depends(get_db)]


async def _get_item(db: AsyncSession, household_id: str, item_id: str) -> PantryItem:
    result = await db.execute(
        select(PantryItem).where(
            PantryItem.item_id == item_id, PantryItem.household_id == household_id
        )
    )
    item = result.scalars().first()
    if item is None:
        raise HTTPException(status_code=404, detail="Pantry item not found")
    return item


@router.get("/pantry", response_model=list[PantryItemSchema])
async def list_pantry(device: DeviceDep, db: DbDep) -> list[PantryItemSchema]:
    household = await get_or_create_household(db, device)
    result = await db.execute(
        select(PantryItem)
        .where(PantryItem.household_id == household.household_id)
        .order_by(PantryItem.name)
    )
    return [PantryItemSchema.model_validate(i) for i in result.scalars().all()]


@router.post("/pantry", response_model=PantryItemSchema, status_code=201)
async def add_pantry_item(
    body: PantryItemCreateRequest, device: DeviceDep, db: DbDep
) -> PantryItemSchema:
    household = await get_or_create_household(db, device)
    count = await db.scalar(
        select(func.count())
        .select_from(PantryItem)
        .where(PantryItem.household_id == household.household_id)
    )
    if (count or 0) >= settings.MAX_PANTRY_ITEMS:
        raise HTTPException(status_code=422, detail="Your pantry is full.")
    item = PantryItem(
        household_id=household.household_id,
        name=body.name,
        category=body.category,
        quantity=body.quantity,
        unit=body.unit,
        status=body.status,
    )
    db.add(item)
    await db.flush()
    return PantryItemSchema.model_validate(item)


@router.put("/pantry/{item_id}", response_model=PantryItemSchema)
async def update_pantry_item(
    item_id: str, body: PantryItemUpdateRequest, device: DeviceDep, db: DbDep
) -> PantryItemSchema:
    household = await get_or_create_household(db, device)
    item = await _get_item(db, household.household_id, item_id)
    if body.name is not None:
        item.name = body.name
    if body.category is not None:
        item.category = body.category
    if body.quantity is not None:
        item.quantity = body.quantity
    if body.unit is not None:
        item.unit = body.unit
    if body.status is not None:
        item.status = body.status
    await db.flush()
    await db.refresh(item)  # reload server-side updated_at within the async context
    return PantryItemSchema.model_validate(item)


@router.delete("/pantry/{item_id}", status_code=204)
async def delete_pantry_item(item_id: str, device: DeviceDep, db: DbDep) -> None:
    household = await get_or_create_household(db, device)
    item = await _get_item(db, household.household_id, item_id)
    await db.delete(item)
    await db.flush()
