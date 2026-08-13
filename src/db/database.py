"""
src/db/database.py - SQLAlchemy engines for AURA's PostgreSQL database.

Two engines are deliberately kept separate:

- `engine` - admin/owner connection.
  Used for database setup and seeding.

- `readonly_engine` - least-privilege connection.
  Used by the NL2SQL pipeline to execute LLM-generated SQL.
  This connection should only have SELECT permission.

The readonly connection is the actual database-level safety boundary.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.settings import settings


# Admin connection.
# Used for setup and seed operations.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


# Read-only connection.
# Used ONLY for executing generated SQL.
readonly_engine = create_engine(
    settings.readonly_database_url(),
    pool_pre_ping=True,
)


def db_reachable(use_readonly=True) -> bool:
    """
    Check whether the selected database connection is reachable.
    """

    target = readonly_engine if use_readonly else engine

    try:
        with target.connect() as conn:
            conn.exec_driver_sql("SELECT 1")

        return True

    except Exception:
        return False