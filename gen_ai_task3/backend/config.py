import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
QDRANT_PATH = os.getenv("QDRANT_PATH", str(BASE_DIR / "qdrant_data"))
HANDBOOK_PATH = os.getenv("HANDBOOK_PATH", str(BASE_DIR / "data" / "university_handbook.pdf"))
TOP_K = int(os.getenv("TOP_K", "3"))

# Verification
if not GROQ_API_KEY:
    print("WARNING: GROQ_API_KEY is not set in environment variables.")
