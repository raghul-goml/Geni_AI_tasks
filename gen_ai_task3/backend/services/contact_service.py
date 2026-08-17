import re
from typing import Dict, Any, Tuple

def validate_contact_request(name: str, email: str, message: str) -> Tuple[bool, str]:
    if not name or len(name.strip()) < 2:
        return False, "Name must be at least 2 characters long."
        
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not email or not re.match(email_regex, email.strip()):
        return False, "Invalid email address format."
        
    if not message or len(message.strip()) < 10:
        return False, "Message must be at least 10 characters long."
        
    return True, ""

def submit_contact_request(name: str, email: str, message: str) -> Dict[str, Any]:
    # Mock submission
    # Log details should be scrubbed or partial to ensure safety
    return {
        "status": "success",
        "message": "Contact request submitted successfully."
    }
