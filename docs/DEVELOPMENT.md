# Development

## Repo layout

```
backend/   FastAPI + async SQLAlchemy + Alembic; Gemini LLM service
  app/
    config.py            all tunables (LLM cost caps, size limits)
    database.py          async engine/session
    ratelimit.py         per-device + global LLM budget
    models/              SQLAlchemy ORM (household, member, goal, schedule,
                         pantry_item, grocery_item, food_item, intent_log,
                         suggestion, feedback)
    schemas/             Pydantic request/response models
    routers/             household, pantry, grocery, intake, suggestions,
                         feedback, history, health
    services/            gemini_service, suggestion_service, household_service
  migrations/            Alembic versions
  tests/                 pytest with mocked Gemini + sqlite
app/       Flutter app
  lib/
    core/ network/ models/ persistence/ input/ services/
    features/ onboarding/ home/ intake/ pantry/ grocery/ suggestions/ history/ settings/
    components/
```

## Identity

No login in v0. Each device generates a UUID (stored in the secure store) and sends it as the
`X-Device-UUID` header. The backend gets-or-creates one household per device. Sign-in
(Apple/Google) is a later phase — the JWT/Apple config in `config.py` is dormant scaffolding.

## How input flows

`POST /intake` takes text and/or a base64 image. `gemini_service.parse_input` (Gemini 2.5
Flash, JSON mode, temp 0.1, thinking disabled) classifies it into structured **intents**.
`pantry_update` and `grocery_add` intents are applied to the DB immediately; everything else
(meal preferences, eat-out notes, etc.) is logged to `intent_logs` for later use. Every input
is stored.

## How suggestions work

`POST /suggestions` assembles the household profile (members, dietary prefs, the single goal,
schedule, current pantry, recent meal requests, and recent feedback) and asks Gemini for a
grocery list (excluding on-hand items, with nutrition estimates) plus cook-with-pantry recipes.
Recent **feedback** is fed back into the prompt so disliked items are avoided — reinforcement
via context, not model training. Results are saved as `suggestions` (also the v0 history).

## Backend dev

```bash
cd backend && source .venv/bin/activate
python -m pytest -q                      # tests (Gemini mocked, sqlite)
uvicorn app.main:app --reload
```

Add a migration after changing a model:

```bash
export DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost/snapfood
alembic revision -m "describe change"    # edit the generated file in migrations/versions
alembic upgrade head
```

## App dev

```bash
cd app
flutter pub get
flutter analyze
flutter run --dart-define=API_BASE_URL=http://localhost:8000   # iOS sim or Android emulator
```

State is `provider` + `ChangeNotifier`; networking goes through `core/services/api_service.dart`
on top of `core/network/api_client.dart` (snake_case JSON, device header). Voice uses on-device
`speech_to_text`; photos use `image_picker`.

## CI/CD

- [`ci.yml`](../.github/workflows/ci.yml) — runs backend `pytest` and `flutter analyze` on
  pushes/PRs.
- [`deploy-mobile.yml`](../.github/workflows/deploy-mobile.yml) — on push to `main` touching
  `app/**`, builds and ships iOS → TestFlight and Android → Play internal via fastlane
  (`app/fastlane/Fastfile`). Required secrets and one-time store setup are in
  [INSTALLATION.md](INSTALLATION.md).

Backend deploy is manual for v0: build the Docker image (`backend/Dockerfile`, which runs
`alembic upgrade head` then uvicorn) and run it on your host.
