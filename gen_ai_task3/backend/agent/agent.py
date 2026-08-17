import time
import json
from typing import Dict, Any, List, Optional
from groq import Groq

from backend.config import GROQ_API_KEY, GROQ_MODEL
from backend.logging_config import logger
from backend.rag.retriever import Retriever
from backend.agent.prompts import SYSTEM_PROMPT
from backend.agent.tools import TOOLS_SCHEMA, execute_tool

# In-memory session store
# Schema: { session_id: { "messages": [...], "pending_action": {...} } }
SESSION_STORE: Dict[str, Dict[str, Any]] = {}

class CampusAgent:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.retriever = Retriever()

    def get_or_create_session(self, session_id: str) -> Dict[str, Any]:
        if session_id not in SESSION_STORE:
            SESSION_STORE[session_id] = {
                "messages": [],
                "pending_action": None
            }
        return SESSION_STORE[session_id]

    def clear_pending_action(self, session: Dict[str, Any]):
        session["pending_action"] = None

    def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
        start_time = time.time()
        session = self.get_or_create_session(session_id)
        
        # 1. Handle confirmation flow if there is a pending contact action
        pending_action = session.get("pending_action")
        if pending_action:
            clean_msg = message.lower().strip()
            confirmations = ["yes", "confirm", "send", "submit", "yes, submit it", "send it", "do it"]
            if any(c in clean_msg for c in confirmations):
                # Execute the confirmed tool
                tool_name = pending_action["tool_name"]
                arguments = pending_action["arguments"]
                
                logger.info(f"action_confirmation | session_id={session_id} | status=confirmed | tool={tool_name}")
                
                tool_start = time.time()
                tool_result = execute_tool(tool_name, arguments)
                tool_time_ms = int((time.time() - tool_start) * 1000)
                logger.info(f"tool_execution | tool={tool_name} | latency_ms={tool_time_ms}")
                
                self.clear_pending_action(session)
                
                # Append completion to history
                session["messages"].append({"role": "user", "content": message})
                ans = "Your request has been successfully submitted! The admissions/administration office will reach out to you soon."
                session["messages"].append({"role": "assistant", "content": ans})
                
                # Truncate history
                if len(session["messages"]) > 12:
                    session["messages"] = session["messages"][-12:]
                    
                return {
                    "answer": ans,
                    "tool": tool_name,
                    "action": {"type": "contact_success", "data": {"status": "submitted"}},
                    "sources": []
                }
            else:
                # Cancel or prompt clarification
                self.clear_pending_action(session)
                session["messages"].append({"role": "user", "content": message})
                ans = "Submission cancelled. Let me know if there is anything else I can help you with."
                session["messages"].append({"role": "assistant", "content": ans})
                
                return {
                    "answer": ans,
                    "tool": None,
                    "action": None,
                    "sources": []
                }

        # 2. RAG Retrieval Step
        # Check if query is handbook-related
        # A simple keyword matcher works reliably here without calling LLM for classification
        handbook_keywords = [
            "attendance", "admission", "revaluation", "exam", "grade", "graduation", 
            "hostel", "scholarship", "rules", "credits", "policy", "handbook", "cgpa", "medical"
        ]
        is_rag_query = any(kw in message.lower() for kw in handbook_keywords)
        
        sources = []
        context_str = ""
        if is_rag_query:
            rag_start = time.time()
            retrieved_chunks = self.retriever.retrieve(message)
            sources = retrieved_chunks
            
            context_blocks = []
            for chunk in retrieved_chunks:
                context_blocks.append(f"Section: {chunk['section']}\nSource: {chunk['source']}\nContent: {chunk['text']}")
            context_str = "\n\n---\n\n".join(context_blocks)
            
            logger.info(f"rag_retrieval_completed | chunks={len(retrieved_chunks)} | latency_ms={int((time.time() - rag_start)*1000)}")

        # 3. Model Inference Setup
        # Prepare system prompt with RAG grounding if applicable
        current_system_prompt = SYSTEM_PROMPT
        if context_str:
            current_system_prompt += f"\n\n### RETRIEVED HANDBOOK CONTEXT\nUse the following official handbook context to answer:\n{context_str}"
            
        messages = [{"role": "system", "content": current_system_prompt}]
        
        # Include session history
        for hist_msg in session["messages"]:
            messages.append(hist_msg)
            
        # Append current user message
        messages.append({"role": "user", "content": message})

        # 4. Invoke LLM with Tool schemas
        llm_start = time.time()
        try:
            response = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto",
                temperature=0.2
            )
        except Exception as e:
            logger.error(f"groq_api_failure | error={str(e)}")
            raise e
            
        llm_latency_ms = int((time.time() - llm_start) * 1000)
        logger.info(f"model_response | model={GROQ_MODEL} | latency_ms={llm_latency_ms}")

        response_message = response.choices[0].message
        
        # 5. Handle LLM Tool Calling Response
        if response_message.tool_calls:
            tool_call = response_message.tool_calls[0]
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            
            logger.info(f"tool_selected | tool={tool_name}")
            
            # Handle high-risk tool call (contact request)
            if tool_name == "submit_contact_request":
                # Do NOT execute tool. Store in session, request confirmation.
                session["pending_action"] = {
                    "tool_name": tool_name,
                    "arguments": arguments
                }
                
                # Scrub message content for logging safety
                scrubbed_args = {
                    "name": arguments.get("name"),
                    "email": "***@***.***",
                    "message": "..."
                }
                logger.info(f"pending_action_created | session_id={session_id} | arguments={scrubbed_args}")
                
                # Update history
                session["messages"].append({"role": "user", "content": message})
                
                name_val = arguments.get("name", "Student")
                email_val = arguments.get("email", "")
                msg_val = arguments.get("message", "")
                
                assistant_answer = (
                    f"I have summarized your contact request:\n\n"
                    f"- **Name**: {name_val}\n"
                    f"- **Email**: {email_val}\n"
                    f"- **Message**: {msg_val}\n\n"
                    f"Please confirm: **Would you like me to submit this contact request?**"
                )
                session["messages"].append({"role": "assistant", "content": assistant_answer})
                
                return {
                    "answer": assistant_answer,
                    "tool": tool_name,
                    "action": {
                        "type": "contact_confirmation",
                        "data": {
                            "name": name_val,
                            "email": email_val,
                            "message": msg_val
                        }
                    },
                    "sources": []
                }
            
            # For other read-only tools, execute immediately
            tool_start = time.time()
            tool_result = execute_tool(tool_name, arguments)
            tool_time_ms = int((time.time() - tool_start) * 1000)
            logger.info(f"tool_execution | tool={tool_name} | latency_ms={tool_time_ms}")
            
            # Construct a response with the tool's result/action payload
            action = tool_result.get("action")
            
            # Append interaction to memory
            session["messages"].append({"role": "user", "content": message})
            
            if tool_name == "search_courses":
                courses = tool_result.get("courses", [])
                if courses:
                    ans = "Here are the matching courses I found in our database:\n"
                    for c in courses:
                        ans += f"- **{c['code']} - {c['name']}**: {c['credits']} credits, Semester {c['semester']} ({c['department']})\n"
                else:
                    ans = "I couldn't find any courses matching your search query."
            elif tool_name == "get_department_info":
                info = tool_result.get("department_info")
                if info:
                    ans = (
                        f"**{info['name']}**\n\n"
                        f"- **Office/Building**: {info['building']}\n"
                        f"- **Contact Email**: {info['email']}\n"
                        f"- **Portal Page**: {info['page']}"
                    )
                    action = {
                        "type": "navigation",
                        "data": {"page": arguments.get("department"), "url": info["page"]}
                    }
                else:
                    ans = tool_result.get("error", "Department not found.")
            elif tool_name == "navigate_page":
                ans = f"Taking you to the {arguments.get('page')} page."
            elif tool_name == "download_handbook":
                ans = "Your download for the official university handbook has started."
            else:
                ans = "Tool execution completed."
                
            session["messages"].append({"role": "assistant", "content": ans})
            
            # Truncate history
            if len(session["messages"]) > 12:
                session["messages"] = session["messages"][-12:]
                
            return {
                "answer": ans,
                "tool": tool_name,
                "action": action,
                "sources": sources
            }
            
        else:
            # Ordinary text response
            answer = response_message.content
            
            # Update history
            session["messages"].append({"role": "user", "content": message})
            session["messages"].append({"role": "assistant", "content": answer})
            
            # Truncate history
            if len(session["messages"]) > 12:
                session["messages"] = session["messages"][-12:]
                
            logger.info(f"request_completed | session_id={session_id} | total_latency_ms={int((time.time() - start_time)*1000)}")
            
            return {
                "answer": answer,
                "tool": None,
                "action": None,
                "sources": sources
            }
