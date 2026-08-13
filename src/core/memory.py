"""
src/core/memory.py - AURA's Memory layer.

- Short-term memory:
  Stores the current conversation and keeps only the latest turns.

- Long-term memory:
  Stores durable facts in a JSON file so they survive across sessions.

- Episodic memory:
  Action history is maintained separately in src/core/tools.py.
"""

import json
import os

from config.settings import BASE_DIR


MEMORY_FILE = os.path.join(
    BASE_DIR,
    "long_term_memory.json",
)

MAX_SHORT_TERM_TURNS = 8


class ShortTermMemory:
    def __init__(self):
        self.turns = []

    def add(self, role, content):
        self.turns.append(
            {
                "role": role,
                "content": content,
            }
        )

        # Keep only the latest N conversation turns.
        if len(self.turns) > MAX_SHORT_TERM_TURNS * 2:
            self.turns = self.turns[-MAX_SHORT_TERM_TURNS * 2:]

    def as_messages(self):
        return list(self.turns)

    def clear(self):
        self.turns = []


def _load_long_term():
    if not os.path.exists(MEMORY_FILE):
        return {}

    with open(
        MEMORY_FILE,
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def _save_long_term(data):
    with open(
        MEMORY_FILE,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            data,
            f,
            indent=2,
        )


def remember(key: str, value: str) -> str:
    """
    Store a durable fact that AURA should remember
    across sessions.
    """

    data = _load_long_term()

    data[key] = value

    _save_long_term(data)

    return f"Remembered: {key} = {value}"


def recall(key: str) -> str:
    """
    Retrieve one previously remembered fact.
    """

    data = _load_long_term()

    return data.get(
        key,
        "(nothing on file for that)",
    )


def recall_all() -> dict:
    """
    Retrieve all long-term memories.
    """

    return _load_long_term()