from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import device_uuid, get_db
from app.models.feedback import Feedback
from app.models.suggestion import Suggestion
from app.schemas.requests import FeedbackRequest
from app.schemas.responses import FeedbackResponse
from app.services.household_service import get_or_create_household

router = APIRouter()

DeviceDep = Annotated[str, Depends(device_uuid)]
DbDep = Annotated[AsyncSession, Depends(get_db)]


@router.post("/feedback", response_model=FeedbackResponse, status_code=201)
async def submit_feedback(
    body: FeedbackRequest, device: DeviceDep, db: DbDep
) -> FeedbackResponse:
    household = await get_or_create_household(db, device)
    suggestion = await db.scalar(
        select(Suggestion).where(
            Suggestion.suggestion_id == body.suggestion_id,
            Suggestion.household_id == household.household_id,
        )
    )
    if suggestion is None:
        raise HTTPException(status_code=404, detail="Suggestion not found")

    fb = Feedback(
        household_id=household.household_id,
        suggestion_id=body.suggestion_id,
        rating=body.rating,
        comment=body.comment,
    )
    db.add(fb)
    await db.flush()
    return FeedbackResponse(
        feedback_id=fb.feedback_id, suggestion_id=fb.suggestion_id, rating=fb.rating
    )
