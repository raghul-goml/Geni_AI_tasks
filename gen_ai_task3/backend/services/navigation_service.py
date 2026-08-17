from typing import Optional, Dict

ALLOWED_PAGES = {
    "home": "/",
    "admissions": "/admissions",
    "courses": "/courses",
    "departments": "/departments",
    "examinations": "/examinations",
    "hostel": "/hostel",
    "scholarships": "/scholarships",
    "student-services": "/student-services",
    "contact": "/contact"
}

def resolve_page_url(page_name: str) -> Optional[str]:
    # Standardize name
    clean_name = page_name.lower().strip().replace(" ", "-")
    return ALLOWED_PAGES.get(clean_name)
