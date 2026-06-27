"""Assemble the household profile, ask Gemini for suggestions, cache nutrition
estimates, and persist the result as a Suggestion (which doubles as history).
"""
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.feedback import Feedback
from app.models.food_item import FoodItem
from app.models.household import Household
from app.models.intent_log import IntentLog
from app.models.pantry_item import PantryItem
from app.models.suggestion import Suggestion
from app.services import gemini_service


async def _pantry_dicts(db: AsyncSession, household_id: str) -> list[dict]:
    result = await db.execute(
        select(PantryItem).where(PantryItem.household_id == household_id)
    )
    return [
        {
            "name": p.name,
            "category": p.category,
            "quantity": float(p.quantity) if p.quantity is not None else None,
            "unit": p.unit,
            "status": p.status,
        }
        for p in result.scalars().all()
    ]


async def _build_profile(db: AsyncSession, household: Household) -> dict:
    pantry = await _pantry_dicts(db, household.household_id)

    intents_res = await db.execute(
        select(IntentLog)
        .where(
            IntentLog.household_id == household.household_id,
            IntentLog.intent_type.in_(["meal_preference", "eat_out_note"]),
        )
        .order_by(IntentLog.created_at.desc())
        .limit(15)
    )
    requests = [
        {"type": i.intent_type, "payload": i.payload, "at": i.created_at.isoformat() if i.created_at else None}
        for i in intents_res.scalars().all()
    ]

    fb_res = await db.execute(
        select(Feedback)
        .where(Feedback.household_id == household.household_id)
        .order_by(Feedback.created_at.desc())
        .limit(15)
    )
    feedback = [
        {"rating": f.rating, "comment": f.comment, "suggestion_id": f.suggestion_id}
        for f in fb_res.scalars().all()
    ]

    return {
        "household": {"name": household.name, "cuisines": household.cuisines or []},
        "members": [
            {"name": m.name, "age": m.age, "dietary_preferences": m.dietary_preferences}
            for m in household.members
        ],
        "dietary": household.dietary_preferences or {},
        "goal": {"description": household.goal.description, "target": household.goal.target}
        if household.goal
        else None,
        "schedule": household.schedule.meals if household.schedule else None,
        "pantry": pantry,
        "requests": requests,
        "feedback": feedback,
    }


async def _cache_nutrition(db: AsyncSession, grocery: list[dict]) -> None:
    """Persist any new nutrition estimates so we can reuse them later."""
    for item in grocery:
        name = (item.get("name") or "").strip()
        nutrition = item.get("nutrition")
        if not name or not nutrition:
            continue
        existing = await db.scalar(select(FoodItem).where(FoodItem.name == name))
        if existing is None:
            db.add(
                FoodItem(
                    name=name,
                    category=item.get("category"),
                    unit=item.get("unit"),
                    nutrition=nutrition,
                )
            )


async def generate(db: AsyncSession, household: Household, kinds: list[str]) -> Suggestion:
    profile = await _build_profile(db, household)
    result = await gemini_service.generate_suggestions(
        today=date.today().isoformat(), profile=profile, kinds=kinds
    )

    grocery = result.get("grocery", []) or []
    await _cache_nutrition(db, grocery)

    payload = {
        "grocery": grocery,
        "recipes": result.get("recipes", []) or [],
        "rationale": result.get("rationale", ""),
        "goal_alignment": result.get("goal_alignment", ""),
        "kinds": kinds,
    }
    kind = "cook_with_pantry" if kinds == ["cook_with_pantry"] else "grocery_list"
    suggestion = Suggestion(household_id=household.household_id, kind=kind, payload=payload)
    db.add(suggestion)
    await db.flush()
    return suggestion
