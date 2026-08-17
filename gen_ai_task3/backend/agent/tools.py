from typing import List, Dict, Any, Optional
from backend.services.course_service import search_courses, get_department_info
from backend.services.navigation_service import resolve_page_url
from backend.services.contact_service import validate_contact_request, submit_contact_request

# Groq-compatible JSON tool schemas
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "search_courses",
            "description": "Search the university course catalog by keyword, code, or department.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query keyword, e.g., 'machine learning' or 'CS101'."
                    },
                    "department": {
                        "type": "string",
                        "description": "Optional department to filter by, e.g., 'Computer Science'."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_department_info",
            "description": "Retrieve information about a specific university department, including its building, email, and contact page.",
            "parameters": {
                "type": "object",
                "properties": {
                    "department": {
                        "type": "string",
                        "description": "Name of the department, e.g., 'Computer Science'."
                    }
                },
                "required": ["department"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "navigate_page",
            "description": "Navigate the user to a specific page on the university portal. Allowed pages: home, admissions, courses, departments, examinations, hostel, scholarships, student-services, contact.",
            "parameters": {
                "type": "object",
                "properties": {
                    "page": {
                        "type": "string",
                        "description": "The destination page identifier."
                    }
                },
                "required": ["page"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "download_handbook",
            "description": "Trigger a download of the official university handbook PDF.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "submit_contact_request",
            "description": "Submit a contact request to the admissions or administration office. This is a high-risk tool that requires explicit user confirmation. Do not call this tool directly without a prior confirmation dialog and immediate user consent.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Full name of the student."
                    },
                    "email": {
                        "type": "string",
                        "description": "Valid email address of the student."
                    },
                    "message": {
                        "type": "string",
                        "description": "The message or question being submitted."
                    }
                },
                "required": ["name", "email", "message"]
            }
        }
    }
]

def execute_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute local python backend services for the tool calls."""
    if name == "search_courses":
        query = arguments.get("query", "")
        dept = arguments.get("department")
        courses = search_courses(query, dept)
        return {"courses": courses}
        
    elif name == "get_department_info":
        dept = arguments.get("department", "")
        info = get_department_info(dept)
        if info:
            return {"department_info": info}
        return {"error": f"Department '{dept}' not found."}
        
    elif name == "navigate_page":
        page = arguments.get("page", "")
        url = resolve_page_url(page)
        if url:
            return {
                "action": {
                    "type": "navigation",
                    "data": {
                        "page": page,
                        "url": url
                    }
                }
            }
        return {"error": f"Page '{page}' is not in the allowed list of pages."}
        
    elif name == "download_handbook":
        return {
            "action": {
                "type": "download",
                "data": {
                    "filename": "university_handbook.pdf",
                    "url": "/downloads/university_handbook.pdf"
                }
            }
        }
        
    elif name == "submit_contact_request":
        # Handled at agent level for confirmation safety,
        # but the actual backend service execution occurs here:
        name_val = arguments.get("name", "")
        email_val = arguments.get("email", "")
        msg_val = arguments.get("message", "")
        
        is_valid, err_msg = validate_contact_request(name_val, email_val, msg_val)
        if not is_valid:
            return {"error": err_msg}
            
        result = submit_contact_request(name_val, email_val, msg_val)
        return result
        
    else:
        return {"error": f"Tool '{name}' is not supported."}
