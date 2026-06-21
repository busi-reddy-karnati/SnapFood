from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.dependencies import device_uuid, get_db
from app.models.grocery_item import GroceryItem
from app.schemas.domain import GroceryItemSchema
from app.schemas.requests import GroceryItemCreateRequest, GroceryItemUpdateRequest
from app.services.household_service import get_or_create_household

router = APIRouter()

DeviceDep = Annotated[str, Depends(device_uuid)]
DbDep = Annotated[AsyncSession, Depends(get_db)]


async def _get_item(db: AsyncSession, household_id: str, item_id: str) -> GroceryItem:
    result = await db.execute(
        select(GroceryItem).where(
            GroceryItem.item_id == item_id, GroceryItem.household_id == household_id
        )
    )
    item = result.scalars().first()
    if item is None:
        raise HTTPException(status_code=404, detail="Grocery item not found")
    return item


@router.get("/grocery", response_model=list[GroceryItemSchema])
async def list_grocery(device: DeviceDep, db: DbDep) -> list[GroceryItemSchema]:
    """Return the active grocery list (removed/purchased items are hidden)."""
    household = await get_or_create_household(db, device)
    result = await db.execute(
        select(GroceryItem)
        .where(
            GroceryItem.household_id == household.household_id,
            GroceryItem.status == "active",
        )
        .order_by(GroceryItem.created_at)
    )
    return [GroceryItemSchema.model_validate(i) for i in result.scalars().all()]


@router.post("/grocery", response_model=GroceryItemSchema, status_code=201)
async def add_grocery_item(
    body: GroceryItemCreateRequest, device: DeviceDep, db: DbDep
) -> GroceryItemSchema:
    household = await get_or_create_household(db, device)
    count = await db.scalar(
        select(func.count())
        .select_from(GroceryItem)
        .where(
            GroceryItem.household_id == household.household_id,
            GroceryItem.status == "active",
        )
    )
    if (count or 0) >= settings.MAX_GROCERY_ITEMS:
        raise HTTPException(status_code=422, detail="Your grocery list is full.")
    item = GroceryItem(
        household_id=household.household_id,
        name=body.name,
        category=body.category,
        quantity=body.quantity,
        unit=body.unit,
        source="manual",
    )
    db.add(item)
    await db.flush()
    return GroceryItemSchema.model_validate(item)


@router.put("/grocery/{item_id}", response_model=GroceryItemSchema)
async def update_grocery_item(
    item_id: str, body: GroceryItemUpdateRequest, device: DeviceDep, db: DbDep
) -> GroceryItemSchema:
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
    return GroceryItemSchema.model_validate(item)


@router.delete("/grocery/{item_id}", status_code=204)
async def delete_grocery_item(item_id: str, device: DeviceDep, db: DbDep) -> None:
    """Soft-remove: mark the item removed so it drops off the active list."""
    household = await get_or_create_household(db, device)
    item = await _get_item(db, household.household_id, item_id)
    item.status = "removed"
    await db.flush()
