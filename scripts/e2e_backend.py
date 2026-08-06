"""Playwright E2E backend runner.

Resets the isolated E2E database (drop schema, recreate, seed) and then
serves the FastAPI app on a dedicated port so that frontend E2E tests never
touch the production database or the regular dev server.

Usage:
    python scripts/e2e_backend.py

Environment:
    E2E_DB_NAME   - test database name (default: milk_management_e2e)
    E2E_PORT      - port to serve the API on (default: 8001)
    DATABASE_URL  - optional full override; wins over E2E_DB_NAME

The in-memory report cache is disabled so E2E assertions always read fresh data.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

E2E_DB_NAME = os.getenv("E2E_DB_NAME", "milk_management_e2e")
E2E_PORT = int(os.getenv("E2E_PORT", "8001"))
DB_USER = os.getenv("E2E_DB_USER", "postgres")
DB_PASSWORD = os.getenv("E2E_DB_PASSWORD", "admin")
DB_HOST = os.getenv("E2E_DB_HOST", "localhost")
DB_PORT = os.getenv("E2E_DB_PORT", "5432")

DEFAULT_DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{E2E_DB_NAME}"
)

os.environ.setdefault("DATABASE_URL", DEFAULT_DATABASE_URL)
os.environ.setdefault("REPORT_CACHE_DISABLED", "1")
os.environ.setdefault("AI_LLM_DISABLED", "1")


def ensure_database_exists() -> None:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

    conn = psycopg2.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        dbname="postgres",
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (E2E_DB_NAME,))
            if cur.fetchone() is None:
                cur.execute(f'CREATE DATABASE "{E2E_DB_NAME}"')
                print(f"Created database {E2E_DB_NAME}")
    finally:
        conn.close()


def reset_database() -> None:
    from app.database import Base, engine
    import app.models  # noqa: F401  (registers all models on Base.metadata)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print(f"Recreated schema in {E2E_DB_NAME}")


def seed_database() -> None:
    from scripts.seed import seed

    seed()


def main() -> None:
    ensure_database_exists()
    reset_database()
    seed_database()

    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=E2E_PORT, reload=False)


if __name__ == "__main__":
    main()
