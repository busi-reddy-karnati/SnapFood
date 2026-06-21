from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import device_uuid, get_db
from app.models.suggestion import Suggestion
from app.ratelimit import enforce_llm_budget
from app.schemas.domain import SuggestionSchema
from app.schemas.requests import SuggestionGenerateRequest
from app.services import suggestion_service
from app.services.household_service import get_or_create_household

router = APIRouter()

DeviceDep = Annotated[str, Depends(device_uuid)]
DbDep = Annotated[AsyncSession, Depends(get_db)]


@router.post(
    "/suggestions",
    response_model=SuggestionSchema,
    dependencies=[Depends(enforce_llm_budget)],
)
async def create_suggestions(
    body: SuggestionGenerateRequest, device: DeviceDep, db: DbDep
) -> SuggestionSchema:
    household = await get_or_create_household(db, device)
    suggestion = await suggestion_service.generate(db, household, body.kinds)
    return SuggestionSchema.model_validate(suggestion)


@router.get("/suggestions", response_model=list[SuggestionSchema])
async def list_suggestions(device: DeviceDep, db: DbDep) -> list[SuggestionSchema]:
    household = await get_or_create_household(db, device)
    result = await db.execute(
        select(Suggestion)
        .where(Suggestion.household_id == household.household_id)
        .order_by(Suggestion.created_at.desc())
        .limit(50)
    )
    return [SuggestionSchema.model_validate(s) for s in result.scalars().all()]
