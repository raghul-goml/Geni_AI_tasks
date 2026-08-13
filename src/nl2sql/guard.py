"""
src/nl2sql/guard.py

Text-level safety checks for LLM-generated SQL.

This is the first line of defense. The actual database safety
boundary is the read-only PostgreSQL connection.
"""

import re


BANNED_KEYWORDS = (
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "TRUNCATE",
    "GRANT",
    "REVOKE",
    "ATTACH",
    "COPY",
    "VACUUM",
    "REPLACE",
    "EXEC",
    "CALL",
)

BANNED_RE = re.compile(
    r"\b(" + "|".join(BANNED_KEYWORDS) + r")\b",
    re.IGNORECASE,
)


class UnsafeSQLError(ValueError):
    pass


def validate_select_only(sql: str) -> str:
    """
    Validate that the generated SQL contains exactly one
    read-only SELECT statement.
    """

    cleaned = sql.strip()

    if not cleaned:
        raise UnsafeSQLError("empty query")

    # Allow one trailing semicolon.
    body = cleaned[:-1].strip() if cleaned.endswith(";") else cleaned

    # Reject multiple SQL statements.
    if ";" in body:
        raise UnsafeSQLError(
            "multiple statements are not allowed "
            "(found an embedded ';')"
        )

    # Only SELECT or WITH ... SELECT is allowed.
    if not re.match(
        r"^\s*(SELECT|WITH)\b",
        body,
        re.IGNORECASE,
    ):
        raise UnsafeSQLError(
            "only a single SELECT (or WITH ... SELECT) "
            "statement is allowed"
        )

    # Reject dangerous SQL keywords.
    banned = BANNED_RE.search(body)

    if banned:
        raise UnsafeSQLError(
            f"'{banned.group(1).upper()}' "
            "is not allowed in a read-only query"
        )

    return body