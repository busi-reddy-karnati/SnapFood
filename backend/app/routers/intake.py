import base64
import binascii
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.dependencies import device_uuid, get_db
from app.models.grocery_item import GroceryItem
from app.models.intent_log import IntentLog
from app.models.pantry_item import PantryItem
from app.ratelimit import enforce_llm_budget
from app.schemas.requests import IntakeRequest
from app.schemas.responses import IntakeResponse
from app.services import gemini_service
from app.services.household_service import get_or_create_household

router = APIRouter()

DeviceDep = Annotated[str, Depends(device_uuid)]
DbDep = Annotated[AsyncSession, Depends(get_db)]


def _decode_image(b64: str) -> bytes:
    try:
        raw = base64.b64decode(b64, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(status_code=422, detail="That image couldn't be read.") from exc
    if len(raw) > settings.MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="That image is too large.")
    return raw


async def _apply_pantry_update(db: AsyncSession, household_id: str, intent: dict) -> str | None:
    name = (intent.get("name") or "").strip()
    if not name:
        return None
    existing = await db.scalar(
        select(PantryItem).where(
            PantryItem.household_id == household_id,
            func.lower(PantryItem.name) == name.lower(),
        )
    )
    status = intent.get("status") or "ok"
    if existing is None:
        db.add(
            PantryItem(
                household_id=household_id,
                name=name,
                category=intent.get("category"),
                quantity=intent.get("quantity"),
                unit=intent.get("unit"),
                status=status if status in {"ok", "low", "out"} else "ok",
            )
        )
        return f"Added {name} to pantry ({status})"
    existing.status = status if status in {"ok", "low", "out"} else existing.status
    if intent.get("quantity") is not None:
        existing.quantity = intent["quantity"]
    if intent.get("unit"):
        existing.unit = intent["unit"]
    if intent.get("category"):
        existing.category = intent["category"]
    return f"Updated {name} in pantry ({existing.status})"


async def _apply_grocery_add(db: AsyncSession, household_id: str, intent: dict) -> str | None:
    name = (intent.get("name") or "").strip()
    if not name:
        return None
    existing = await db.scalar(
        select(GroceryItem).where(
            GroceryItem.household_id == household_id,
            GroceryItem.status == "active",
            func.lower(GroceryItem.name) == name.lower(),
        )
    )
    if existing is not None:
        return None  # already on the list
    db.add(
        GroceryItem(
            household_id=household_id,
            name=name,
            category=intent.get("category"),
            quantity=intent.get("quantity"),
            unit=intent.get("unit"),
            source="suggested",
        )
    )
    return f"Added {name} to grocery list"


@router.post("/intake", response_model=IntakeResponse, dependencies=[Depends(enforce_llm_budget)])
async def intake(body: IntakeRequest, device: DeviceDep, db: DbDep) -> IntakeResponse:
    if not body.text and not body.image_base64:
        raise HTTPException(status_code=422, detail="Provide text or an image.")

    image_bytes = _decode_image(body.image_base64) if body.image_base64 else None
    household = await get_or_create_household(db, device)
    pantry = [
        {"name": p.name, "category": p.category, "status": p.status}
        for p in (
            await db.execute(
                select(PantryItem).where(PantryItem.household_id == household.household_id)
            )
        ).scalars().all()
    ]

    parsed = await gemini_service.parse_input(
        today=date.today().isoformat(),
        raw_text=body.text,
        image_bytes=image_bytes,
        image_mime=body.image_mime,
        dietary=household.dietary_preferences or {},
        pantry=pantry,
    )

    intents: list[dict] = parsed.get("intents", []) or []
    applied: list[str] = []
    for intent in intents:
        itype = intent.get("type")
        if itype == "pantry_update":
            msg = await _apply_pantry_update(db, household.household_id, intent)
        elif itype == "grocery_add":
            msg = await _apply_grocery_add(db, household.household_id, intent)
        else:
            msg = None  # meal_preference / eat_out_note / etc. are logged only
        if msg:
            applied.append(msg)

    primary_type = intents[0].get("type") if intents else "unknown"
    log = IntentLog(
        household_id=household.household_id,
        source="image" if image_bytes is not None else "text",
        raw_text=body.text,
        has_image=image_bytes is not None,
        intent_type=primary_type,
        payload={"summary": parsed.get("summary", ""), "intents": intents},
    )
    db.add(log)
    await db.flush()

    return IntakeResponse(
        intent_id=log.intent_id,
        intent_type=primary_type,
        intents=intents,
        applied=applied,
        message=parsed.get("summary") or "Got it.",
    )
