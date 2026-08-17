import sys
from pathlib import Path

# Add backend directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from pypdf import PdfReader
from backend.config import HANDBOOK_PATH
from backend.rag.chunker import semantic_chunk_text
from backend.rag.indexer import Indexer

def run_ingestion():
    pdf_path = Path(HANDBOOK_PATH)
    if not pdf_path.exists():
        print(f"Error: Handbook PDF not found at {pdf_path}. Please generate it or place it there.")
        sys.exit(1)
        
    print(f"Reading PDF from {pdf_path}...")
    reader = PdfReader(pdf_path)
    
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"
            
    # Clean whitespace
    full_text = "\n".join([line.strip() for line in full_text.splitlines() if line.strip()])
    
    print("Chunking document...")
    chunks = semantic_chunk_text(full_text, source_name="university_handbook.pdf")
    print(f"Generated {len(chunks)} chunks.")
    
    print("Initializing Qdrant indexer...")
    indexer = Indexer()
    
    print("Indexing documents into Qdrant Local...")
    indexer.index_chunks(chunks)
    print("Ingestion completed successfully!")

if __name__ == "__main__":
    run_ingestion()
