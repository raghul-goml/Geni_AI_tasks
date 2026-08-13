"""
scripts/seed_db.py - populates Ben 10 & Raghul's learning and well-being progress table
from the deterministic rows in src/db/seed_data.py.
"""

from src.db.database import SessionLocal
from src.db.models import LearningProgress
from src.db.seed_data import LEARNING_PROGRESS


def main():
    session = SessionLocal()

    try:
        # Clear existing learning progress data
        session.query(LearningProgress).delete()
        session.flush()

        # Insert current learning progress data
        for row in LEARNING_PROGRESS:
            session.add(
                LearningProgress(
                    topic=row["topic"],
                    category=row["category"],
                    status=row["status"],
                    progress=row["progress"],
                    notes=row["notes"],
                )
            )

        session.commit()

        print(
            f"Seeded {len(LEARNING_PROGRESS)} learning progress records."
        )

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


if __name__ == "__main__":
    main()