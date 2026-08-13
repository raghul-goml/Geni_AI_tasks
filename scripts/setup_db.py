"""
scripts/setup_db.py - creates Ben 10 & Plumber structured database tables
and the least-privilege read-only PostgreSQL role.
"""

import re
import sys

from sqlalchemy import text

from config.settings import settings
from src.db.database import engine
from src.db.models import Base


ROLE_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def main():
    role = settings.READONLY_DB_USER

    if not ROLE_NAME_RE.match(role):
        sys.exit(
            f"READONLY_DB_USER '{role}' is not a safe SQL identifier - aborting."
        )

    password_literal = settings.READONLY_DB_PASSWORD.replace("'", "''")

    # Create all tables defined in src/db/models.py.
    Base.metadata.create_all(engine)

    print(
        "Tables ensured: "
        + ", ".join(t.name for t in Base.metadata.sorted_tables)
    )

    with engine.begin() as conn:
        db_name = conn.execute(
            text("SELECT current_database()")
        ).scalar()

        # Check whether the readonly role already exists.
        exists = conn.execute(
            text(
                "SELECT 1 FROM pg_roles "
                "WHERE rolname = :role"
            ),
            {"role": role},
        ).first()

        if exists:
            conn.execute(
                text(
                    f"ALTER ROLE {role} "
                    f"WITH LOGIN PASSWORD '{password_literal}'"
                )
            )

            print(
                f"Read-only role '{role}' already existed - "
                "password refreshed."
            )

        else:
            conn.execute(
                text(
                    f"CREATE ROLE {role} "
                    f"WITH LOGIN PASSWORD '{password_literal}'"
                )
            )

            print(f"Created read-only role: {role}")

        # Allow the readonly role to connect to the database.
        conn.execute(
            text(
                f'GRANT CONNECT ON DATABASE "{db_name}" TO {role}'
            )
        )

        # Allow access to the public schema.
        conn.execute(
            text(
                f"GRANT USAGE ON SCHEMA public TO {role}"
            )
        )

        # Grant SELECT permission on every table defined
        # in SQLAlchemy metadata.
        for table in Base.metadata.sorted_tables:
            conn.execute(
                text(
                    f"GRANT SELECT ON {table.name} TO {role}"
                )
            )

        print(
            f"Granted SELECT-only access on "
            f"{len(Base.metadata.sorted_tables)} table(s) "
            f"to '{role}'."
        )

    print("\nDatabase is up to date.")


if __name__ == "__main__":
    main()