from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.dependencies import device_uuid, get_db
from app.models.goal import Goal
from app.models.household import Household
from app.models.member import Member
from app.models.schedule import Schedule
from app.schemas.domain import GoalSchema, MemberSchema, ScheduleSchema
from app.schemas.requests import (
    GoalUpdateRequest,
    HouseholdUpdateRequest,
    MemberCreateRequest,
    MemberUpdateRequest,
    ScheduleUpdateRequest,
)
from app.schemas.responses import HouseholdResponse
from app.services.household_service import get_or_create_household

router = APIRouter()

DeviceDep = Annotated[str, Depends(device_uuid)]
DbDep = Annotated[AsyncSession, Depends(get_db)]


def _to_response(h: Household) -> HouseholdResponse:
    return HouseholdResponse(
        household_id=h.household_id,
        name=h.name,
        dietary_preferences=h.dietary_preferences or {},
        cuisines=h.cuisines or [],
        goal=GoalSchema.model_validate(h.goal) if h.goal else None,
        schedule=ScheduleSchema.model_validate(h.schedule) if h.schedule else None,
        members=[MemberSchema.model_validate(m) for m in h.members],
    )


@router.get("/household", response_model=HouseholdResponse)
async def get_household(device: DeviceDep, db: DbDep) -> HouseholdResponse:
    household = await get_or_create_household(db, device)
    return _to_response(household)


@router.put("/household", response_model=HouseholdResponse)
async def update_household(
    body: HouseholdUpdateRequest, device: DeviceDep, db: DbDep
) -> HouseholdResponse:
    household = await get_or_create_household(db, device)
    if body.name is not None:
        household.name = body.name
    if body.dietary_preferences is not None:
        household.dietary_preferences = body.dietary_preferences
    if body.cuisines is not None:
        household.cuisines = body.cuisines
    await db.flush()
    return _to_response(household)


# --- Members ----------------------------------------------------------- #
# Mutate the loaded `household.members` collection directly so the response
# reflects the change (a re-query would return the identity-mapped household
# with its already-loaded, stale collection).
def _find_member(household: Household, member_id: str) -> Member:
    for m in household.members:
        if m.member_id == member_id:
            return m
    raise HTTPException(status_code=404, detail="Member not found")


@router.post("/household/members", response_model=HouseholdResponse, status_code=201)
async def add_member(
    body: MemberCreateRequest, device: DeviceDep, db: DbDep
) -> HouseholdResponse:
    household = await get_or_create_household(db, device)
    if len(household.members) >= settings.MAX_MEMBERS:
        raise HTTPException(status_code=422, detail="Too many household members.")
    member = Member(
        name=body.name,
        age=body.age,
        dietary_preferences=body.dietary_preferences,
        notes=body.notes,
    )
    household.members.append(member)
    await db.flush()
    return _to_response(household)


@router.put("/household/members/{member_id}", response_model=HouseholdResponse)
async def update_member(
    member_id: str, body: MemberUpdateRequest, device: DeviceDep, db: DbDep
) -> HouseholdResponse:
    household = await get_or_create_household(db, device)
    member = _find_member(household, member_id)
    if body.name is not None:
        member.name = body.name
    if body.age is not None:
        member.age = body.age
    if body.dietary_preferences is not None:
        member.dietary_preferences = body.dietary_preferences
    if body.notes is not None:
        member.notes = body.notes
    await db.flush()
    return _to_response(household)


@router.delete("/household/members/{member_id}", response_model=HouseholdResponse)
async def delete_member(
    member_id: str, device: DeviceDep, db: DbDep
) -> HouseholdResponse:
    household = await get_or_create_household(db, device)
    member = _find_member(household, member_id)
    household.members.remove(member)  # delete-orphan cascade removes the row
    await db.flush()
    return _to_response(household)


# --- Goal (single per household) --------------------------------------- #
@router.put("/household/goal", response_model=GoalSchema)
async def set_goal(body: GoalUpdateRequest, device: DeviceDep, db: DbDep) -> GoalSchema:
    household = await get_or_create_household(db, device)
    if household.goal is None:
        goal = Goal(description=body.description, target=body.target)
        household.goal = goal
    else:
        goal = household.goal
        goal.description = body.description
        goal.target = body.target
    await db.flush()
    return GoalSchema.model_validate(goal)


# --- Schedule ---------------------------------------------------------- #
@router.put("/household/schedule", response_model=ScheduleSchema)
async def set_schedule(
    body: ScheduleUpdateRequest, device: DeviceDep, db: DbDep
) -> ScheduleSchema:
    household = await get_or_create_household(db, device)
    if household.schedule is None:
        schedule = Schedule(meals=body.meals)
        household.schedule = schedule
    else:
        schedule = household.schedule
        schedule.meals = body.meals
    await db.flush()
    return ScheduleSchema.model_validate(schedule)
