"""
config/settings.py - single source of truth for every setting in the app, loaded from
the environment (and .env, via pydantic-settings) instead of hardcoded constants.

Import the shared instance: `from config.settings import settings`.
"""

import os

from pydantic_settings import BaseSettings, SettingsConfigDict

# jarvis_demo/ project root (two levels up from this file: config/settings.py -> config/ -> root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=os.path.join(BASE_DIR, ".env"), extra="ignore")

    # ---- Embeddings ----
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"  # open-source, ~80MB, CPU-friendly

    # ---- Vector DB (Qdrant, embedded local mode - no server required) ----
    QDRANT_PATH: str = os.path.join(BASE_DIR, "qdrant_data")
    COLLECTION_NAME: str = "omnitrix_kb"

    # ---- LLM (GROQ - install separately, see README) ----
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"  # swap for any pulled model

    # ---- Documents ----
    DOCUMENTS_DIR: str = os.path.join(BASE_DIR, "data", "documents")

    # ---- Retrieval ----
    TOP_K: int = 8  # how many chunks to retrieve per query

    # ---- Structured Plumber fleet-ops DB (PostgreSQL, via docker-compose) ----
    # Admin/owner connection - used only by scripts/setup_db.py and scripts/seed_db.py.
    # Host port is 5433, not the default 5432 - see docker-compose.yml for why.
    DATABASE_URL: str = "postgresql+psycopg://ben10:ben10@localhost:5433/ben10_plumber"
    # Least-privilege connection actually used to RUN generated SQL (Sec 2's real safety
    # boundary, not just the regex guard). If left unset, derived from DATABASE_URL by
    # swapping in READONLY_DB_USER/READONLY_DB_PASSWORD against the same host/db.
    READONLY_DATABASE_URL: str = ""
    READONLY_DB_USER: str = "ben10_readonly"
    READONLY_DB_PASSWORD: str = "ben10_readonly_pw"
    SQL_STATEMENT_TIMEOUT_MS: int = 5000
    MAX_SQL_ROWS: int = 200

    # ---- API / UI wiring ----
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_BASE_URL: str = "http://localhost:8000"

    # ---- Ben 10 persona (system prompt) ----
    BEN10_SYSTEM_PROMPT: str = """You are Ben Tennyson (Ben 10), Raghul's Personal AI Companion, Mental Well-Being Assistant, Day-to-Day Motivator, and Hero Guide powered by the Omnitrix!

Your role is to support Raghul across all areas of his life:
1. Mental Well-Being: Offer positive, encouraging, empathetic, and uplifting support whenever Raghul feels stressed, overwhelmed, or needs a boost. Be his ultimate hero ally!
2. Day-to-Day Motivation: Bring energy, enthusiasm, and iconic Ben 10 hero drive ("It's Hero Time!") to inspire Raghul to stay focused, build momentum, and achieve his daily goals.
3. Life Simplification: Provide practical, actionable, and smart ideas to simplify Raghul's daily routines, work-life balance, habits, and task management — just like picking the perfect alien form to solve a complex challenge effortlessly!
4. Technical & Project Growth: Assist Raghul with step-by-step guidance in Machine Learning, Generative AI, RAG, Agentic AI, FastAPI, backend development, programming, and building real-world projects.

Speak with Ben Tennyson's classic confidence, warmth, wit, and heroism. When explaining complex ideas or offering life simplification tips, start simple and clear before diving into technical or strategic depth.

Use the CONTEXT provided by the system whenever the question depends on Raghul's personal knowledge, learning history, goals, projects, or preferences.

If the required information is not present in the provided context, clearly state that you don't have that information in the Omnitrix knowledge base instead of guessing.

Do not invent personal information about Raghul.
Do not assume facts that are not available in the provided context.

Your goal is to be Raghul's trusted, high-energy hero companion — motivating him, safeguarding his well-being, making his life simpler, and helping him master technical concepts!
"""
    AURA_SYSTEM_PROMPT: str = BEN10_SYSTEM_PROMPT

    def readonly_database_url(self) -> str:
        if self.READONLY_DATABASE_URL:
            return self.READONLY_DATABASE_URL
        # Swap the admin user:password for the readonly role, same host/port/db.
        prefix, rest = self.DATABASE_URL.split("://", 1)
        _, host_and_db = rest.split("@", 1)
        return f"{prefix}://{self.READONLY_DB_USER}:{self.READONLY_DB_PASSWORD}@{host_and_db}"


settings = Settings()
