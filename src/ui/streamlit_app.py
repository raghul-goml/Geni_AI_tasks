"""
src/ui/streamlit_app.py

Streamlit chat interface for Ben 10 AI Assistant.

Two modes:
- RAG: answers using retrieved knowledge only (Omnitrix Knowledge Base)
- Agentic: uses ReAct agent + tools + memory + structured DB

Run from project root:

streamlit run src/ui/streamlit_app.py
"""

import os
import sys
import uuid

import requests
import streamlit as st


# -------------------------------------------------------------------
# Project root
# -------------------------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

sys.path.insert(0, PROJECT_ROOT)


from config.settings import settings


API_BASE_URL = settings.API_BASE_URL


# -------------------------------------------------------------------
# Page configuration
# -------------------------------------------------------------------

st.set_page_config(
    page_title="Ben 10 AI Assistant",
    page_icon="⌚",
    layout="centered",
)


# -------------------------------------------------------------------
# Session state
# -------------------------------------------------------------------

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "mode" not in st.session_state:
    st.session_state.mode = "RAG"

if "history" not in st.session_state:
    st.session_state.history = {
        "RAG": [],
        "Agentic": [],
    }


# -------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------

def reset_conversation():
    """
    Clear the conversation for the currently selected mode.
    """

    mode_key = (
        "rag"
        if st.session_state.mode == "RAG"
        else "agent"
    )

    try:
        requests.delete(
            f"{API_BASE_URL}/api/v1/chat/session/"
            f"{st.session_state.session_id}",
            params={"mode": mode_key},
            timeout=5,
        )
    except requests.exceptions.RequestException:
        pass

    st.session_state.history[
        st.session_state.mode
    ] = []


def get_health():
    """
    Get backend health information.
    """

    try:
        response = requests.get(
            f"{API_BASE_URL}/health",
            timeout=5,
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException:
        return None


# -------------------------------------------------------------------
# Sidebar
# -------------------------------------------------------------------

with st.sidebar:

    st.title("⌚ Ben 10 AI")

    st.caption(
        "Raghul's Hero Motivator & Life Simplifier"
    )

    # Mode selection
    mode = st.radio(
        "Mode",
        ["RAG", "Agentic"],
        index=(
            0
            if st.session_state.mode == "RAG"
            else 1
        ),
        help=(
            "RAG answers using retrieved knowledge. "
            "Agentic mode can use tools, memory, "
            "and the structured learning & well-being database."
        ),
    )

    if mode != st.session_state.mode:
        st.session_state.mode = mode

    st.divider()

    # ---------------------------------------------------------------
    # System status
    # ---------------------------------------------------------------

    st.subheader("Omnitrix Status")

    health = get_health()

    api_ok = health is not None

    st.write(
        ("🟢" if api_ok else "⚠️")
        + " API "
        + (
            "reachable"
            if api_ok
            else "not reachable"
        )
    )

    if not api_ok:
        st.caption(
            f"Could not reach {API_BASE_URL}. "
            "Make sure the FastAPI server is running."
        )

    # Knowledge base
    kb_ok = bool(
        health
        and health.get("knowledge_base")
    )

    st.write(
        ("🟢" if kb_ok else "⚠️")
        + " Omnitrix Knowledge Base "
        + (
            "ready"
            if kb_ok
            else "not ready"
        )
    )

    if api_ok and not kb_ok:
        st.caption(
            "Run `python -m scripts.ingest` "
            "from the project root."
        )

    # Groq / LLM
    llm_ok = bool(
        health
        and (
            health.get("groq")
            or health.get("llm")
        )
    )

    st.write(
        ("🟢" if llm_ok else "⚠️")
        + " Groq LLM Core "
        + (
            "reachable"
            if llm_ok
            else "not reachable"
        )
    )

    if api_ok and not llm_ok:
        st.caption(
            "Check your Groq API configuration "
            "and backend environment variables."
        )

    # PostgreSQL
    postgres_ok = bool(
        health
        and health.get("postgres")
    )

    st.write(
        ("🟢" if postgres_ok else "⚠️")
        + " Plumber Database "
        + (
            "reachable"
            if postgres_ok
            else "not reachable"
        )
    )

    if api_ok and not postgres_ok:
        st.caption(
            "Make sure PostgreSQL is running and "
            "the database is configured correctly."
        )

    st.divider()

    # Clear conversation
    if st.button(
        "Clear conversation",
        use_container_width=True,
    ):
        reset_conversation()
        st.rerun()

    st.divider()

    st.caption(
        "Ben 10 powered by RAG, Agentic AI, "
        "Omnitrix memory, Groq, Qdrant, "
        "and PostgreSQL for Raghul."
    )


# -------------------------------------------------------------------
# Main chat area
# -------------------------------------------------------------------

st.header(
    f"Chat with Ben 10 — "
    f"{st.session_state.mode} mode"
)

if st.session_state.mode == "RAG":

    st.caption(
        "Ben 10 answers using retrieved knowledge "
        "from the Omnitrix knowledge base."
    )

else:

    st.caption(
        "Ben 10 can reason, call tools, use memory, "
        "query Raghul's well-being database, and perform "
        "heroic simulated actions. It's Hero Time!"
    )


# -------------------------------------------------------------------
# Render Agent trace
# -------------------------------------------------------------------

def render_trace(trace):
    """
    Display ReAct Thought -> Action -> Observation trace.
    """

    if not trace:
        return

    with st.expander(
        "See Ben 10's reasoning "
        "(Thought → Action → Observation)"
    ):

        for i, step in enumerate(
            trace,
            1,
        ):

            st.markdown(
                f"**Step {i} - Thought:** "
                f"{step.get('thought', '')}"
            )

            action = step.get("action")

            if (
                action
                and action.lower() != "none"
            ):

                st.markdown(
                    f"**Action:** "
                    f"`{action}"
                    f"({step.get('action_input', {})})`"
                )

            observation = step.get(
                "observation"
            )

            if observation:

                st.markdown(
                    f"**Observation:** "
                    f"{observation}"
                )

            if i < len(trace):

                st.markdown("---")


# -------------------------------------------------------------------
# Render previous messages
# -------------------------------------------------------------------

current_history = st.session_state.history[
    st.session_state.mode
]

for message in current_history:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )

        if message.get("meta"):
            st.caption(
                message["meta"]
            )

        if message.get("trace"):
            render_trace(
                message["trace"]
            )


# -------------------------------------------------------------------
# Chat input
# -------------------------------------------------------------------

query = st.chat_input(
    "Ask Ben 10 something..."
)


# -------------------------------------------------------------------
# Process user query
# -------------------------------------------------------------------

if query:

    # Save user message
    st.session_state.history[
        st.session_state.mode
    ].append(
        {
            "role": "user",
            "content": query,
        }
    )

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):

        # -----------------------------------------------------------
        # Basic health checks
        # -----------------------------------------------------------

        if not api_ok:

            st.error(
                f"Cannot reach Ben 10 API at "
                f"{API_BASE_URL}."
            )

        elif not kb_ok:

            st.warning(
                "Omnitrix Knowledge base is not ready. "
                "Run `python -m scripts.ingest` first."
            )

        elif not llm_ok:

            st.warning(
                "Groq / LLM is not available. "
                "Check the backend configuration."
            )

        else:

            with st.spinner(
                "Ben 10 is transforming & thinking..."
            ):

                endpoint = (
                    "rag"
                    if st.session_state.mode == "RAG"
                    else "agent"
                )

                try:

                    response = requests.post(
                        f"{API_BASE_URL}"
                        f"/api/v1/chat/{endpoint}",
                        json={
                            "session_id": (
                                st.session_state.session_id
                            ),
                            "query": query,
                        },
                        timeout=120,
                    )

                    response.raise_for_status()

                    data = response.json()

                except requests.exceptions.RequestException as e:

                    st.error(
                        f"Request to Ben 10 API failed: {e}"
                    )

                    data = None

                # ---------------------------------------------------
                # Response
                # ---------------------------------------------------

                if data:

                    reply = data.get(
                        "reply",
                        "Ben 10 did not return a response.",
                    )

                    st.markdown(reply)

                    # ------------------------------------------------
                    # RAG mode
                    # ------------------------------------------------

                    if (
                        st.session_state.mode
                        == "RAG"
                    ):

                        citations = data.get(
                            "citations"
                        ) or []

                        meta = None

                        if citations:

                            meta = (
                                "Retrieved from: "
                                + ", ".join(citations)
                            )

                            st.caption(meta)

                        st.session_state.history[
                            "RAG"
                        ].append(
                            {
                                "role": "assistant",
                                "content": reply,
                                "meta": meta,
                            }
                        )

                    # ------------------------------------------------
                    # Agentic mode
                    # ------------------------------------------------

                    else:

                        trace = (
                            data.get("trace")
                            or []
                        )

                        render_trace(trace)

                        st.session_state.history[
                            "Agentic"
                        ].append(
                            {
                                "role": "assistant",
                                "content": reply,
                                "trace": trace,
                            }
                        )