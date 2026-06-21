from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import (
    feedback,
    grocery,
    health,
    history,
    household,
    intake,
    pantry,
    suggestions,
)

app = FastAPI(
    title="SnapFood API",
    version="0.1.0",
    description="Backend API for the SnapFood household meal-planning app",
)

# Friendly, single-string `detail` for input-cap violations so the app can show
# the real reason instead of Pydantic's raw error list.
_TOO_LONG_MESSAGES = {
    "text": "That input is too long. Please keep it shorter.",
    "image_base64": "That image is too large. Try a smaller one.",
    "comment": "That comment is too long. Please shorten it and try again.",
}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    for err in exc.errors():
        if err.get("type") in {"string_too_long", "too_long"}:
            field = err["loc"][-1] if err.get("loc") else None
            detail = _TOO_LONG_MESSAGES.get(field, "That input is too long.")
            return JSONResponse(status_code=422, content={"detail": detail})
    first = exc.errors()[0] if exc.errors() else {}
    return JSONResponse(
        status_code=422,
        content={"detail": first.get("msg", "Your request couldn't be processed.")},
    )


@app.middleware("http")
async def limit_request_body_size(request: Request, call_next):
    """Reject oversized requests up front (Content-Length) before reading the
    body, protecting against memory/DB abuse via giant payloads."""
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > settings.MAX_REQUEST_BODY_BYTES:
                return JSONResponse(
                    status_code=413, content={"detail": "That request is too large."}
                )
        except ValueError:
            pass
    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(household.router, prefix="/api/v1")
app.include_router(pantry.router, prefix="/api/v1")
app.include_router(grocery.router, prefix="/api/v1")
app.include_router(intake.router, prefix="/api/v1")
app.include_router(suggestions.router, prefix="/api/v1")
app.include_router(feedback.router, prefix="/api/v1")
app.include_router(history.router, prefix="/api/v1")
