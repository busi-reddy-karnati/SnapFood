from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import device_uuid, get_db
from app.models.suggestion import Suggestion
from app.schemas.domain import SuggestionSchema
from app.schemas.responses import HistoryResponse
from app.services.household_service import get_or_create_household

router = APIRouter()

DeviceDep = Annotated[str, Depends(device_uuid)]
DbDep = Annotated[AsyncSession, Depends(get_db)]


@router.get("/history", response_model=HistoryResponse)
async def get_history(device: DeviceDep, db: DbDep) -> HistoryResponse:
    """Past suggestions / grocery lists (the v0 stand-in for order history)."""
    household = await get_or_create_household(db, device)
    result = await db.execute(
        select(Suggestion)
        .where(Suggestion.household_id == household.household_id)
        .order_by(Suggestion.created_at.desc())
        .limit(100)
    )
    return HistoryResponse(
        suggestions=[SuggestionSchema.model_validate(s) for s in result.scalars().all()]
    )
