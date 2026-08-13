"""
src/core/agent.py - Ben 10's Agentic AI layer.

Combines:
- LLM reasoning
- Tools
- Short-term memory
- ReAct planning loop

Architecture:
Think -> Act -> Observe -> Repeat -> Final Answer
"""

import json
import re

from config.settings import settings
from src.core.llm import chat
from src.core.tools import (
    TOOL_REGISTRY,
    tool_descriptions_block,
    run_tool,
)
from src.core.memory import ShortTermMemory


BEN10_SYSTEM_PROMPT = getattr(settings, "BEN10_SYSTEM_PROMPT", settings.AURA_SYSTEM_PROMPT)
AURA_SYSTEM_PROMPT = BEN10_SYSTEM_PROMPT

MAX_ITERATIONS = 5


REACT_INSTRUCTIONS = f"""
You are Ben Tennyson operating in AGENTIC mode with Omnitrix tactical support.

You can use tools when they are necessary to answer the user's
request or perform a safe action.

Use the ReAct pattern:

Think -> Act -> Observe -> Repeat -> Final Answer

Available tools:

{tool_descriptions_block()}

STRICT OUTPUT FORMAT:

Thought: <what you need to do next>
Action: <one tool name from the available tools, or "none">
Action Input: <valid JSON arguments>

If you have enough information to answer, use:

Thought: <final reasoning>
Action: none
Action Input: {{}}
Final Answer: <your final answer to the user>

Rules:

- Call only ONE tool per turn.
- Never skip the Thought line.
- Action must be one of the registered tools or "none".
- Action Input must always be valid JSON.
- Use {{}} when the selected tool requires no arguments.
- Do not invent tool names.
- Use lookup_knowledge_base for information stored in the
  semantic knowledge base.
- Use query_learning_progress for exact structured learning
  progress information.
- Use remember_fact when the user explicitly asks you to
  remember something.
- Use recall_fact when a previously remembered fact is needed.
- Use schedule_reminder only for reminder requests.
- Use view_action_log when the user asks what actions were
  performed during the current session.
- Do not claim that an action was performed unless the tool
  returned a successful result.
"""


BLOCK_RE = re.compile(
    r"Thought:\s*(?P<thought>.*?)\s*"
    r"Action:\s*(?P<action>.*?)\s*"
    r"Action Input:\s*(?P<action_input>\{.*?\}|\{\})"
    r"(?:.*?Final Answer:\s*(?P<final>.*?))?$",
    re.DOTALL,
)


def _parse_step(text):
    """
    Parse one ReAct response from the LLM.
    """

    match = BLOCK_RE.search(text.strip())

    if not match:
        return {
            "thought": "format not followed",
            "action": "none",
            "action_input": {},
            "final": text.strip(),
        }

    action = match.group("action").strip()

    try:
        action_input = json.loads(
            match.group("action_input").strip()
        )
    except json.JSONDecodeError:
        action_input = {}

    final = match.group("final")

    return {
        "thought": match.group("thought").strip(),
        "action": action,
        "action_input": action_input,
        "final": final.strip() if final else None,
    }


def run_agent(
    query,
    short_term: ShortTermMemory,
    verbose=True,
):
    """
    Run the ReAct agent loop for one user query.

    Returns:

        final_answer, trace

    trace contains the Thought -> Action -> Observation
    sequence for the UI.
    """

    messages = [
        {
            "role": "system",
            "content": (
                AURA_SYSTEM_PROMPT
                + "\n\n"
                + REACT_INSTRUCTIONS
            ),
        }
    ]

    # Add previous conversation.
    messages.extend(
        short_term.as_messages()
    )

    # Add current user question.
    messages.append(
        {
            "role": "user",
            "content": query,
        }
    )

    trace = []

    for i in range(MAX_ITERATIONS):

        # Ask Groq/LLM to decide the next step.
        raw = chat(
            messages,
            temperature=0.2,
        )

        step = _parse_step(raw)

        if verbose:
            print(
                f"\n[Planning step {i + 1}] "
                f"Thought: {step['thought']}"
            )

        # If the LLM already has the final answer,
        # stop the loop.
        if step["final"]:
            trace.append(
                {
                    "thought": step["thought"],
                    "action": "none",
                    "action_input": {},
                    "observation": None,
                    "final": True,
                }
            )

            return step["final"], trace

        action = step["action"]

        entry = {
            "thought": step["thought"],
            "action": action,
            "action_input": step["action_input"],
            "observation": None,
            "final": False,
        }

        # Execute a registered tool.
        if (
            action
            and action.lower() != "none"
            and action in TOOL_REGISTRY
        ):

            if verbose:
                print(
                    f"[Planning step {i + 1}] "
                    f"Action: {action}"
                    f"({step['action_input']})"
                )

            try:
                observation = run_tool(
                    action,
                    **step["action_input"],
                )

            except Exception as e:
                observation = (
                    f"ERROR running tool "
                    f"'{action}': {e}"
                )

            if verbose:
                print(
                    f"[Planning step {i + 1}] "
                    f"Observation: {observation}"
                )

            entry["observation"] = observation

            trace.append(entry)

            # Give the LLM the tool result.
            messages.append(
                {
                    "role": "assistant",
                    "content": raw,
                }
            )

            messages.append(
                {
                    "role": "user",
                    "content": (
                        f"Observation: {observation}\n\n"
                        "Continue with the next "
                        "Thought/Action, or provide "
                        "your Final Answer."
                    ),
                }
            )

        else:

            trace.append(entry)

            messages.append(
                {
                    "role": "assistant",
                    "content": raw,
                }
            )

            messages.append(
                {
                    "role": "user",
                    "content": (
                        "Please provide your Final Answer now."
                    ),
                }
            )

    return (
        "Ben 10 has reached the planning limit for this "
        "request. Please try breaking the request into "
        "smaller steps.",
        trace,
    )