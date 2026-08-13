"""
src/ui/cli.py - command-line entry point for the JARVIS demo (the Streamlit app in
streamlit_app.py is the primary interface - this CLI is kept for quick terminal testing).

A THIN HTTP CLIENT of src/api, same as the Streamlit app - run the API first:
    uvicorn src.api.main:app --reload --port 8000

Usage (from the project root):
    python -m src.ui.cli --mode rag      # RAG only - JARVIS replies, never acts
    python -m src.ui.cli --mode agent    # Agentic - JARVIS can call tools and take action

Type 'exit' or 'quit' to leave.
"""

import argparse
import sys
import uuid

import requests

from config.settings import settings

API_BASE_URL = settings.API_BASE_URL

BANNER = r"""
    ____  ______ _   __  _______   ____ 
   / __ )/ ____// | / / / / ___/  / __ \
  / __  / __/  /  |/ / / / __ \  / / / /
 / /_/ / /___ / /|  / / / /_/ / / /_/ / 
/_____/_____//_/ |_/ /_/\____/  \____/  
"""


def _post_chat(endpoint, session_id, query):
    resp = requests.post(
        f"{API_BASE_URL}/api/v1/chat/{endpoint}",
        json={"session_id": session_id, "query": query},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()


def run_rag_mode():
    print(BANNER)
    print("BEN 10 (RAG mode) online. It's Hero Time! I can answer from my Omnitrix knowledge base.")
    print("Type 'exit' to quit.\n")
    session_id = str(uuid.uuid4())

    while True:
        query = input("You: ").strip()
        if query.lower() in ("exit", "quit"):
            print("BEN 10: It's Hero Time! Catch you later, Raghul!")
            break
        if not query:
            continue
        try:
            data = _post_chat("rag", session_id, query)
        except requests.exceptions.RequestException as e:
            print(f"\n[SETUP ISSUE] Could not reach the API at {API_BASE_URL}: {e}\n")
            continue

        print(f"\nBEN 10: {data['reply']}\n")
        if data.get("citations"):
            print("  (retrieved from: " + ", ".join(data["citations"]) + ")\n")


def run_agent_mode():
    print(BANNER)
    print("BEN 10 (AGENTIC mode) online. It's Hero Time! I can look things up in the Omnitrix & Plumber "
          "database AND take hero action now.")
    print("Type 'exit' to quit.\n")
    session_id = str(uuid.uuid4())

    while True:
        query = input("You: ").strip()
        if query.lower() in ("exit", "quit"):
            print("BEN 10: It's Hero Time! Catch you later, Raghul!")
            break
        if not query:
            continue
        try:
            data = _post_chat("agent", session_id, query)
        except requests.exceptions.RequestException as e:
            print(f"\n[SETUP ISSUE] Could not reach the API at {API_BASE_URL}: {e}\n")
            continue

        print(f"\nBEN 10: {data['reply']}\n")


def main():
    parser = argparse.ArgumentParser(description="Ben 10 AI Assistant CLI (RAG or Agentic mode)")
    parser.add_argument("--mode", choices=["rag", "agent"], default="rag", help="Which capability to demo")
    args = parser.parse_args()

    if args.mode == "rag":
        run_rag_mode()
    else:
        run_agent_mode()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBEN 10: It's Hero Time! Catch you later!")
        sys.exit(0)
