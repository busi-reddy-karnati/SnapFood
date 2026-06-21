# SnapFood

SnapFood plans meals for your household. Tell it what you need by **text, voice, or photo**
("rice is almost over, order it next time", "I want lamb next week") and it tracks your
pantry, dietary preferences, and goal, then suggests **what to cook with what you have** and
builds an editable **grocery list**.

> **v0:** no ordering yet — SnapFood suggests groceries/recipes and prepares a list you can
> edit. Real ordering (DoorDash) is planned for a later phase.

## Stack

- **App:** Flutter (Android + iOS), in [`app/`](app/)
- **Backend:** FastAPI + PostgreSQL, LLM via Google Gemini, in [`backend/`](backend/)
- **CI/CD:** push to `main` ships both apps (iOS → TestFlight, Android → Play internal)

## Docs

- [Installation](docs/INSTALLATION.md) — run the backend and app locally; one-time store setup
- [Development](docs/DEVELOPMENT.md) — architecture, tests, migrations, and the CI/CD flow
