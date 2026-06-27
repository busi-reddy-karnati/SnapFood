# Installation

## Quick Start (Make)

The fastest way to get SnapFood running locally is with `make`:

```
make setup        # first-time: venv, deps, migrate, seed, flutter pub get
make backend-bg   # start backend in background
make emulator     # start Android emulator
make run-app      # build and run SnapFood on the emulator
make health       # verify backend is up
```

See all available targets with `make help` or read the `Makefile` at the repo root.

## Prerequisites

- Python 3.12+
- PostgreSQL 14+
- Flutter SDK (stable channel) with Xcode (iOS) and/or Android SDK
- A Google Gemini API key

## Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env            # then set GEMINI_API_KEY and DATABASE_URL
createdb snapfood               # or point DATABASE_URL at an existing Postgres

export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost/snapfood"
alembic upgrade head            # create the schema
uvicorn app.main:app --reload   # serves on http://localhost:8000
```

Health check: `curl http://localhost:8000/api/v1/health` → `{"status":"ok"}`.

### Seed data (optional)

Populate the database with a demo household, pantry, and grocery list:

```bash
cd backend
source .venv/bin/activate
pip install psycopg2-binary
python seed.py
```

This is idempotent — it is safe to run multiple times.

## App

```bash
cd app
flutter pub get
flutter create --platforms=ios,android .   # one-time: generate native runners

# run against your local backend (use your machine IP for a real device)
flutter run --dart-define=API_BASE_URL=http://localhost:8000
```

After `flutter create`, add these permissions once (they survive future builds):

- **iOS** — `ios/Runner/Info.plist`:
  ```xml
  <key>NSMicrophoneUsageDescription</key><string>SnapFood uses the mic to capture what you need.</string>
  <key>NSSpeechRecognitionUsageDescription</key><string>SnapFood transcribes your voice on-device.</string>
  <key>NSCameraUsageDescription</key><string>SnapFood reads food items from photos.</string>
  <key>NSPhotoLibraryUsageDescription</key><string>SnapFood reads food items from your photos.</string>
  ```
- **Android** — `android/app/src/main/AndroidManifest.xml` (inside `<manifest>`):
  ```xml
  <uses-permission android:name="android.permission.INTERNET"/>
  <uses-permission android:name="android.permission.RECORD_AUDIO"/>
  <uses-permission android:name="android.permission.CAMERA"/>
  ```

## One-time setup for CI deploys

The [deploy workflow](../.github/workflows/deploy-mobile.yml) needs these to exist first:

- **App Store Connect:** create the app record with bundle id `com.snapfood.app`; create an
  API key (for `ASC_KEY_ID` / `ASC_ISSUER_ID` / `ASC_KEY_P8_BASE64`); export your distribution
  certificate as `.p12` (for `BUILD_CERTIFICATE_BASE64` / `P12_PASSWORD`).
- **Google Play:** create the app + package `com.snapfood.app` and upload one build manually so
  the package exists; create a service account with Play API access (`PLAY_SERVICE_ACCOUNT_JSON`);
  generate an upload keystore (`ANDROID_KEYSTORE_BASE64` + passwords/alias).
- **Shared:** set `API_BASE_URL` to your production backend.

Add all of the above as GitHub repository **secrets**. After that, every push to `main` that
touches `app/**` ships to TestFlight and the Play internal track automatically.
