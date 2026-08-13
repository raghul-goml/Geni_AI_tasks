"""
src/nl2sql/generator.py

Turns a natural-language question into a candidate SQL query.

The generated SQL is untrusted until it passes the SQL safety
guard and executes through the read-only database connection.
"""

import re

from src.core.llm import chat


SQL_SYSTEM_PROMPT = """You are a SQL generator for a PostgreSQL database.

Given the schema below and a user's question, write EXACTLY ONE
read-only SELECT statement that answers the question.

Rules:

- Output ONLY the SQL query.
- No prose, explanation, or markdown code fences.
- Only a single SELECT or WITH ... SELECT statement.
- Never use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE,
  or any other write operation.
- Use ONLY the tables and columns listed in the schema.
- Never invent a table or column.
- Prefer simple and accurate SQL.
- If the question cannot be answered from the provided schema,
  output exactly: NO_QUERY

Important semantic rules for the learning_progress table:

- status = 'learning' means the topic is currently being learned.
- status = 'completed' means the topic has been completed.
- If the user asks "current learning progress", "currently learning",
  "what am I learning", or similar wording, interpret it as
  status = 'learning'.
- If the user asks about completed topics, use status = 'completed'.
- Use the progress column to report percentage progress.
- Do not invent status values such as 'current', 'active', or 'in_progress'
  when they are not present in the schema/data.
"""


FENCE_RE = re.compile(
    r"```(?:sql)?\s*(.*?)```",
    re.IGNORECASE | re.DOTALL,
)


def _extract_sql(raw: str) -> str:
    """
    Remove markdown SQL fences if the LLM adds them accidentally.
    """

    match = FENCE_RE.search(raw)

    if match:
        return match.group(1).strip()

    return raw.strip()


def generate_sql(
    question: str,
    schema_description: str,
    previous_sql: str = None,
    retry_feedback: str = None,
) -> str:
    """
    Generate one candidate SQL query from a natural-language question.
    """

    messages = [
        {
            "role": "system",
            "content": (
                SQL_SYSTEM_PROMPT
                + "\n\nDATABASE SCHEMA:\n"
                + schema_description
            ),
        },
        {
            "role": "user",
            "content": question,
        },
    ]

    # If the first SQL attempt was rejected by the safety guard,
    # ask the LLM to correct it.
    if retry_feedback:
        messages.append(
            {
                "role": "assistant",
                "content": previous_sql or "",
            }
        )

        messages.append(
            {
                "role": "user",
                "content": (
                    f"That SQL query was rejected because: "
                    f"{retry_feedback}\n\n"
                    "Generate a corrected query. "
                    "Output ONLY one SELECT statement."
                ),
            }
        )

    raw = chat(
        messages,
        temperature=0.0,
    )

    return _extract_sql(raw)