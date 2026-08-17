import re
from typing import List, Dict, Any

def semantic_chunk_text(text: str, source_name: str) -> List[Dict[str, Any]]:
    # Known logical headings/sections in our handbook
    headings = [
        "Academic Regulations",
        "Admissions",
        "Attendance Policy",
        "Examinations and Revaluation",
        "Hostel Rules",
        "Scholarships",
        "Departments and CS Department",
        "Student Services"
    ]
    
    # Let's split the text by these headings
    # Create regex pattern matching any of these headings
    pattern = "|".join([re.escape(h) for h in headings])
    splits = re.split(f"({pattern})", text)
    
    chunks = []
    
    # If the text does not start with a heading, the first block is intro
    current_section = "General Information"
    
    i = 0
    if len(splits) > 1 and splits[0].strip() == "":
        i = 1
        
    while i < len(splits):
        part = splits[i].strip()
        if part in headings:
            current_section = part
            i += 1
            if i < len(splits):
                content = splits[i].strip()
                # If content is very long, sub-chunk it
                sub_chunks = split_into_sub_chunks(content, max_chars=1200)
                for idx, sub_txt in enumerate(sub_chunks):
                    chunks.append({
                        "section": current_section,
                        "text": f"[{current_section}]\n{sub_txt}",
                        "source": source_name,
                        "chunk_id": f"{current_section.lower().replace(' ', '_')}_{idx}"
                    })
        else:
            if part:
                sub_chunks = split_into_sub_chunks(part, max_chars=1200)
                for idx, sub_txt in enumerate(sub_chunks):
                    chunks.append({
                        "section": current_section,
                        "text": f"[{current_section}]\n{sub_txt}",
                        "source": source_name,
                        "chunk_id": f"{current_section.lower().replace(' ', '_')}_{idx}"
                    })
        i += 1
        
    return chunks

def split_into_sub_chunks(text: str, max_chars: int = 1200) -> List[str]:
    # Simple semantic splitter by paragraphs or sentences
    paragraphs = text.split("\n\n")
    sub_chunks = []
    current_chunk = []
    current_length = 0
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if current_length + len(para) > max_chars and current_chunk:
            sub_chunks.append("\n\n".join(current_chunk))
            current_chunk = [para]
            current_length = len(para)
        else:
            current_chunk.append(para)
            current_length += len(para) + 2
            
    if current_chunk:
        sub_chunks.append("\n\n".join(current_chunk))
        
    return sub_chunks
