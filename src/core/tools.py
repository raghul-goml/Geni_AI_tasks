"""
src/core/tools.py - Ben 10's agentic Tools layer.

Each tool has one clearly defined responsibility.
The agent can use these tools to retrieve knowledge,
query structured learning data, manage memory, and
perform simulated low-risk actions.
"""

from datetime import datetime

from src.core.vector_store import retrieve
from src.core.rag import format_context
from src.nl2sql.pipeline import answer as nl2sql_answer
import src.core.memory as memory_module


# Session-level episodic action log.
ACTION_LOG = []


def tool_lookup_knowledge_base(query: str) -> str:
    """
    Read-only tool.

    Searches Ben 10's Omnitrix Qdrant knowledge base for relevant
    personal knowledge and returns the retrieved context.
    """

    chunks = retrieve(query, top_k=4)

    return format_context(chunks)


def tool_query_learning_progress(question: str) -> str:
    """
    Read-only tool.

    Uses the NL2SQL pipeline to answer exact questions
    about the structured learning_progress database table.
    """

    result = nl2sql_answer(question)

    if result.get("error"):
        return (
            "Could not safely answer from the learning "
            f"database: {result['error']}"
        )

    return (
        f"SQL used: {result['sql']}\n\n"
        f"Answer: {result['answer']}"
    )


def tool_schedule_reminder(
    text: str,
    when: str = "unspecified time",
) -> str:
    """
    Low-risk simulated action.

    Does not create a real notification.
    It only records the requested reminder in the
    session action log.
    """

    timestamp = datetime.now().strftime("%H:%M:%S")

    entry = (
        f"[{timestamp}] "
        f"HERO REMINDER SET for {when}: {text}"
    )

    ACTION_LOG.append(entry)

    print(f"\n  >> {entry}\n")

    return (
        f"Reminder set for {when}: '{text}'"
    )


def tool_view_action_log() -> str:
    """
    Read-only tool.

    Shows hero actions performed during the current session.
    """

    if not ACTION_LOG:
        return "No actions taken yet this session."

    return "\n".join(ACTION_LOG)


def tool_remember_fact(
    key: str,
    value: str,
) -> str:
    """
    Low-risk tool.

    Stores a durable fact in Ben 10's long-term memory.
    """

    return memory_module.remember(
        key,
        value,
    )


def tool_recall_fact(key: str) -> str:
    """
    Read-only tool.

    Retrieves a previously stored fact from
    Ben 10's long-term memory.
    """

    return memory_module.recall(key)


# ------------------------------------------------------------------
# Tool Registry
# ------------------------------------------------------------------
#
# name -> function + description + risk + confirmation requirement
#
# The agent uses this registry to discover what capabilities
# are available.
# ------------------------------------------------------------------

TOOL_REGISTRY = {

    "lookup_knowledge_base": {
        "fn": tool_lookup_knowledge_base,
        "description": (
            "Search Ben 10's Omnitrix knowledge base for "
            "relevant information. Use for semantic or "
            "narrative questions. Read-only."
        ),
        "risk": "none",
        "confirm": False,
    },

    "query_learning_progress": {
        "fn": tool_query_learning_progress,
        "description": (
            "Query the structured learning_progress database "
            "for exact counts, progress values, statuses, "
            "categories, or other structured learning data. "
            "Read-only."
        ),
        "risk": "none",
        "confirm": False,
    },

    "schedule_reminder": {
        "fn": tool_schedule_reminder,
        "description": (
            "Schedule a simulated reminder with text and "
            "optional time. No real notification is sent. "
            "Low-risk and reversible."
        ),
        "risk": "low",
        "confirm": False,
    },

    "view_action_log": {
        "fn": tool_view_action_log,
        "description": (
            "View hero actions performed by Ben 10 during the "
            "current session. Read-only."
        ),
        "risk": "none",
        "confirm": False,
    },

    "remember_fact": {
        "fn": tool_remember_fact,
        "description": (
            "Store a durable personal fact in Ben 10's "
            "long-term memory. Low-risk."
        ),
        "risk": "low",
        "confirm": False,
    },

    "recall_fact": {
        "fn": tool_recall_fact,
        "description": (
            "Recall a previously stored personal fact "
            "from Ben 10's long-term memory. Read-only."
        ),
        "risk": "none",
        "confirm": False,
    },
}


def _signature_hint(name):
    """
    Provides argument hints for the agent's tool prompt.
    """

    hints = {
        "lookup_knowledge_base": "query",
        "query_learning_progress": "question",
        "schedule_reminder": (
            "text, when='unspecified time'"
        ),
        "view_action_log": "",
        "remember_fact": "key, value",
        "recall_fact": "key",
    }

    return hints.get(name, "")


def tool_descriptions_block():
    """
    Build the tool description block used by the
    agent's ReAct system prompt.
    """

    lines = []

    for name, spec in TOOL_REGISTRY.items():
        lines.append(
            f"- {name}({_signature_hint(name)}): "
            f"{spec['description']}"
        )

    return "\n".join(lines)


def run_tool(name, **kwargs):
    """
    Execute a registered tool by name.
    """

    if name not in TOOL_REGISTRY:
        return (
            f"ERROR: no such tool '{name}'. "
            f"Available tools: "
            f"{', '.join(TOOL_REGISTRY.keys())}"
        )

    return TOOL_REGISTRY[name]["fn"](**kwargs)