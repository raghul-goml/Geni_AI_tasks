"""
src/core/llm.py - thin wrapper around Groq API.

Groq is used as the LLM provider for AURA.
"""

from groq import Groq

from config.settings import settings


GROQ_API_KEY = settings.GROQ_API_KEY
GROQ_MODEL = settings.GROQ_MODEL


class GroqUnavailable(RuntimeError):
    pass


client = Groq(api_key=GROQ_API_KEY)


def chat(messages, temperature=0.4, model=None):
    """
    Send chat messages to Groq and return the assistant's reply.

    messages:
        List of dictionaries with:
        {"role": "system" | "user" | "assistant", "content": str}

    temperature:
        Controls response randomness.

    model:
        Optional model override. If not provided, the configured
        GROQ_MODEL is used.
    """

    model = model or GROQ_MODEL

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )

    except Exception as exc:
        raise GroqUnavailable(
            "Could not reach Groq or complete the request.\n"
            "Check your GROQ_API_KEY and internet connection."
        ) from exc

    return response.choices[0].message.content


def groq_alive():
    """
    Check whether the Groq API is reachable.
    """
    try:
        # A lightweight request using the Groq client.
        # If the API key is invalid or unavailable, this returns False.
        from groq import Groq

        client = Groq(
            api_key=settings.GROQ_API_KEY
        )

        client.models.list()

        return True

    except Exception:
        return False