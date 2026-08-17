from typing import List, Dict, Any, Optional

COURSES_DB = [
    {
        "code": "CS101",
        "name": "Introduction to Computer Science",
        "department": "Computer Science",
        "credits": 3,
        "semester": 1
    },
    {
        "code": "CS201",
        "name": "Data Structures",
        "department": "Computer Science",
        "credits": 4,
        "semester": 3
    },
    {
        "code": "CS301",
        "name": "Artificial Intelligence",
        "department": "Computer Science",
        "credits": 3,
        "semester": 5
    },
    {
        "code": "DS301",
        "name": "Machine Learning",
        "department": "Computer Science",
        "credits": 3,
        "semester": 5
    },
    {
        "code": "EC201",
        "name": "Digital Electronics",
        "department": "Electronics",
        "credits": 3,
        "semester": 3
    }
]

DEPARTMENTS_DB = {
    "computer science": {
        "name": "Computer Science & Engineering",
        "building": "Turing Block",
        "email": "cs@university.edu",
        "page": "/departments"
    },
    "electronics": {
        "name": "Electronics & Communication Engineering",
        "building": "Shannon Block",
        "email": "ece@university.edu",
        "page": "/departments"
    }
}

def search_courses(query: str, department: Optional[str] = None) -> List[Dict[str, Any]]:
    query = query.lower()
    results = []
    for course in COURSES_DB:
        # Filter by department if specified
        if department and course["department"].lower() != department.lower():
            continue
        
        # Search match in code or name
        if query in course["name"].lower() or query in course["code"].lower() or query in course["department"].lower():
            results.append(course)
            
    return results

def get_department_info(department: str) -> Optional[Dict[str, Any]]:
    dep_key = department.lower().strip()
    # check for substrings or exact keys
    for k, v in DEPARTMENTS_DB.items():
        if k in dep_key or dep_key in k:
            return v
    return None
