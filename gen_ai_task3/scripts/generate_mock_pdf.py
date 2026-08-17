import os
from pathlib import Path

def generate_pdf():
    data_dir = Path(__file__).resolve().parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    pdf_path = data_dir / "university_handbook.pdf"

    # Define the text sections
    sections = [
        ("Official University Handbook", "This is the official university handbook containing academic regulations, policies, and details."),
        ("Academic Regulations", "Graduation Requirements: Students must successfully complete a minimum of 180 credits to graduate. All core course credits must be completed with a cumulative grade point average (CGPA) of at least 2.0. Students must complete their program within a maximum of six years from the date of admission."),
        ("Admissions", "Admission Documents: The following documents are required for admission to any undergraduate program: 1. High School Transcript and Passing Certificate. 2. Proof of Identity (Passport or National ID Card). 3. Two Reference Letters from academic referees. 4. A completed Application Form. 5. Proof of English Proficiency (TOEFL or IELTS) if English is not the native language."),
        ("Attendance Policy", "Attendance Requirement: The minimum attendance requirement for students to be eligible to appear in the end-semester examinations is 75% for each registered course. Shortage of attendance up to 10% can be condoned by the Dean on medical grounds, supported by valid medical certificates. Students with attendance below 65% will not be allowed to sit for examinations under any circumstances."),
        ("Examinations and Revaluation", "Revaluation Process: Students who are not satisfied with their grades in the final examination can apply for revaluation of their answer scripts. The revaluation application must be submitted online to the Office of Examinations within 15 days of the declaration of results. A non-refundable revaluation fee of $50 per course is applicable. The revaluation process takes approximately 14 working days, and the updated grade, whether higher or lower, will be final."),
        ("Hostel Rules", "Hostel Policies: All hostel residents must adhere to the curfew timing of 10:00 PM. External guests are permitted in the hostel common areas only between 8:00 AM and 8:00 PM and are strictly prohibited in student rooms. Cooking inside hostel rooms is strictly prohibited. Noise levels must be kept to a minimum during quiet hours from 9:00 PM to 7:00 AM."),
        ("Scholarships", "Scholarship Programs: The university offers Merit Scholarships to students who achieve a GPA of 3.80 or higher in their previous semester. These merit scholarships offer a 50% tuition waiver for the subsequent semester. Financial Need Scholarships are also available for students coming from low-income families, providing up to 100% waiver depending on documentation of household income."),
        ("Departments and CS Department", "Computer Science Department: The Department of Computer Science and Engineering is located in the Turing Block, Room 301. The office hours are Monday to Friday, 9:00 AM to 5:00 PM. For general inquiries, students can contact the department office at cs@university.edu. The department offers state-of-the-art labs and research opportunities in Artificial Intelligence, Machine Learning, and Cybersecurity."),
        ("Student Services", "Academic Counseling and Support: Student Services offers comprehensive academic counseling, mental health counseling, and career guidance. The campus health clinic is open 24/7 for medical emergencies. Students can access tutoring services at the Student Success Center located in the Central Library, Room 102.")
    ]

    # Let's generate a valid PDF by constructing the PDF tree manually
    # We will write the text using PDF operators
    
    # We will use BT (Begin Text) / ET (End Text), Tf (Font), Td (Move text position), Tj (Show text)
    # Let's format the text with line wraps so it fits on pages
    stream_content = []
    stream_content.append("BT")
    stream_content.append("/F1 20 Tf")
    stream_content.append("1 0 0 1 50 750 Tm")
    stream_content.append("(Official University Handbook) Tj")
    stream_content.append("/F2 10 Tf")
    stream_content.append("0 -20 Td")
    stream_content.append("(This is the official university handbook containing academic regulations, policies, and details.) Tj")
    stream_content.append("0 -30 Td")

    for title, text in sections[1:]:
        stream_content.append("/F1 14 Tf")
        stream_content.append(f"({title}) Tj")
        stream_content.append("0 -18 Td")
        
        # Simple line wrap helper (max 80 chars per line)
        stream_content.append("/F2 10 Tf")
        words = text.split(" ")
        line = ""
        for word in words:
            if len(line) + len(word) + 1 < 80:
                line += (" " if line else "") + word
            else:
                # Escape parentheses for PDF
                safe_line = line.replace("(", "\\(").replace(")", "\\)")
                stream_content.append(f"({safe_line}) Tj")
                stream_content.append("0 -13 Td")
                line = word
        if line:
            safe_line = line.replace("(", "\\(").replace(")", "\\)")
            stream_content.append(f"({safe_line}) Tj")
            stream_content.append("0 -22 Td")

    stream_content.append("ET")
    
    stream_bytes = "\n".join(stream_content).encode("latin-1")
    
    # PDF objects
    objects = []
    
    # Object 1: Catalog
    # Object 2: Pages
    # Object 3: Page
    # Object 4: Font 1 (Helvetica-Bold)
    # Object 5: Font 2 (Helvetica)
    # Object 6: Content Stream
    
    body = []
    offsets = {}
    
    def add_object(obj_str):
        obj_id = len(objects) + 1
        offsets[obj_id] = len(b"".join(body)) + 9  # 9 is for '%PDF-1.4\n'
        obj_bytes = f"{obj_id} 0 obj\n{obj_str}\nendobj\n".encode("latin-1")
        body.append(obj_bytes)
        objects.append(obj_bytes)
        return obj_id

    # Construct the PDF file bytes
    # Header
    pdf_header = b"%PDF-1.4\n"
    
    # We define placeholders for objects, then construct them in order
    catalog_id = 1
    pages_id = 2
    page_id = 3
    font1_id = 4
    font2_id = 5
    stream_id = 6
    
    # Catalog
    add_object(f"<< /Type /Catalog /Pages {pages_id} 0 R >>")
    # Pages
    add_object(f"<< /Type /Pages /Kids [ {page_id} 0 R ] /Count 1 >>")
    # Page
    add_object(f"<< /Type /Page /Parent {pages_id} 0 R /Resources << /Font << /F1 {font1_id} 0 R /F2 {font2_id} 0 R >> >> /MediaBox [0 0 612 792] /Contents {stream_id} 0 R >>")
    # Font 1
    add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    # Font 2
    add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    # Content Stream
    stream_obj = f"<< /Length {len(stream_bytes)} >>\nstream\n".encode("latin-1") + stream_bytes + b"\nendstream"
    add_object(stream_obj.decode("latin-1"))
    
    # Cross-reference table (xref)
    xref_pos = len(pdf_header) + len(b"".join(body))
    xref_str = f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n"
    for obj_id in range(1, len(objects) + 1):
        xref_str += f"{offsets[obj_id]:010d} 00000 n \n"
        
    xref_bytes = xref_str.encode("latin-1")
    
    trailer_str = f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n"
    trailer_bytes = trailer_str.encode("latin-1")
    
    with open(pdf_path, "wb") as f:
        f.write(pdf_header)
        f.write(b"".join(body))
        f.write(xref_bytes)
        f.write(trailer_bytes)
        
    print(f"Successfully generated pure-python mock PDF at: {pdf_path}")

if __name__ == "__main__":
    generate_pdf()
