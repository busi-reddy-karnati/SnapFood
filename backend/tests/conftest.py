import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app import ratelimit
from app.database import Base
from app.dependencies import get_db
from app.main import app
from app.services import gemini_service, suggestion_service

DEVICE = "11111111-1111-1111-1111-111111111111"


# --- In-memory sqlite shared across the test session ------------------- #
engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def _override_get_db():
    async with TestSession() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest_asyncio.fixture(autouse=True)
async def _setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    app.dependency_overrides[get_db] = _override_get_db
    ratelimit.device_llm_limiter.reset()
    ratelimit.global_llm_limiter.reset()
    yield
    app.dependency_overrides.clear()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# --- Mocked Gemini ----------------------------------------------------- #
async def _fake_parse_input(*, today, raw_text, image_bytes, image_mime, dietary, pantry):
    text = (raw_text or "").lower()
    intents: list[dict] = []
    if "rice" in text:
        intents.append({"type": "pantry_update", "name": "Rice", "category": "grain", "status": "low"})
        if "order" in text or "buy" in text or "restock" in text:
            intents.append({"type": "grocery_add", "name": "Rice", "category": "grain"})
    if "lamb" in text:
        intents.append({"type": "meal_preference", "item": "Lamb", "timeframe": "next week"})
    if "indian" in text:
        intents.append({"type": "eat_out_note", "cuisine": "Indian", "when": "tonight"})
    if image_bytes is not None:
        intents.append({"type": "pantry_update", "name": "Tomatoes", "category": "produce", "status": "ok"})
    if not intents:
        intents.append({"type": "unknown", "note": raw_text})
    return {"summary": "ok", "intents": intents}


async def _fake_generate_suggestions(*, today, profile, kinds):
    # Drop any item the user thumbs-downed (reinforcement wiring).
    disliked = " ".join(
        (f.get("comment") or "").lower()
        for f in profile.get("feedback", [])
        if f.get("rating") == "down"
    )
    grocery = [
        {"name": "Spinach", "category": "produce", "quantity": 1, "unit": "bunch",
         "nutrition": {"calories": 23, "protein_g": 2.9, "fiber_g": 2.2}},
        {"name": "Lentils", "category": "pulse", "quantity": 500, "unit": "g",
         "nutrition": {"calories": 1160, "protein_g": 90, "fiber_g": 45}},
    ]
    grocery = [g for g in grocery if g["name"].lower() not in disliked]
    return {
        "grocery": grocery,
        "recipes": [{"title": "Lentil Spinach Dal", "uses_pantry": ["Rice"], "needs": ["Lentils"]}],
        "rationale": "High protein and fiber toward your goal.",
        "goal_alignment": "Adds protein and fiber.",
    }


@pytest.fixture(autouse=True)
def _mock_gemini(monkeypatch):
    monkeypatch.setattr(gemini_service, "parse_input", _fake_parse_input)
    monkeypatch.setattr(gemini_service, "generate_suggestions", _fake_generate_suggestions)
    # suggestion_service calls gemini_service.generate_suggestions via the module
    # reference, so patching the attribute above is sufficient.
    assert suggestion_service.gemini_service.generate_suggestions is _fake_generate_suggestions


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test/api/v1",
        headers={"X-Device-UUID": DEVICE},
    ) as ac:
        yield ac
