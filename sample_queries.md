# Sample Queries - Ben 10 AI Assistant

Run `python -m scripts.ingest` once, then launch `streamlit run src/ui/streamlit_app.py`
(or use `python -m src.ui.cli --mode rag` / `--mode agent` for terminal testing).

## RAG Mode

RAG should only ever **reply** using retrieved knowledge — it never takes actions directly.

| Query | What it showcases |
|---|---|
| `What is Raghul's primary focus?` | Retrieval from `about_me.txt` — basic profile, well-being & technical goals. |
| `What are Raghul's mental well-being and motivation goals?` | Retrieval from `goals.txt` — mental resilience & daily hero motivation. |
| `How does Ben 10 help simplify Raghul's daily life?` | Retrieval from `goals.txt` and `about_me.txt` — life simplification & productivity strategies. |
| `What is Raghul's current learning progress in Machine Learning and RAG?` | Retrieval from `learning_journey.md` — structured learning progress. |
| `Walk me through the Master Control protocol.` | Retrieval from `protocol_manual.html` — clean HTML section extraction. |

## Agentic Mode

In the Streamlit UI, open the "See Ben 10's reasoning" expander under each reply to
watch the ReAct loop (Thought / Action / Observation).

| Query | What it showcases |
|---|---|
| `What am I currently learning in my structured learning database?` | Tool call: `query_learning_progress` -> generates SQL -> executes against PostgreSQL -> returns exact rows. |
| `Remind me to do a 10-minute mindfulness breathing session tomorrow at 8am.` | Tool call: `schedule_reminder` -> records hero action in episodic log. |
| `Remember that Raghul prefers simple daily routines and positive hero motivation.` | Tool call: `remember_fact` -> writes durable fact to long-term memory (`long_term_memory.json`). |
| `What do you remember about Raghul's preferences?` | Tool call: `recall_fact` -> reads back persisted memory across sessions. |
| `What actions have been performed during this session?` | Tool call: `view_action_log` -> displays session episodic log. |
