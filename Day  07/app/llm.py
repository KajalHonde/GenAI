import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from groq import Groq

# Load .env from the working directory (or any parent) when running locally.
# On Render, env vars are injected by the platform — load_dotenv is a no-op
# there, which is correct.  We also try the sibling Day 06 folder so the
# local dev workflow (running from the repo root) keeps working.
load_dotenv()
_DAY06_ENV = Path(__file__).resolve().parents[2] / "Day 06" / ".env"
if _DAY06_ENV.exists():
    load_dotenv(_DAY06_ENV)


def _call_groq(system_prompt, user_message, api_key, model):
    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        temperature=0.3,
        max_tokens=1024
    )

    answer = response.choices[0].message.content or ""
    usage = response.usage

    return answer, {
        "prompt_tokens": getattr(usage, "prompt_tokens", 0) or 0,
        "completion_tokens": getattr(
            usage, "completion_tokens", 0
        ) or 0,
        "total_tokens": getattr(usage, "total_tokens", 0) or 0,
    }


def _call_gemini(system_prompt, user_message, api_key, model):
    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model=model,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.3,
            max_output_tokens=1024
        )
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    usage = getattr(response, "usage_metadata", None)

    def _count(name):
        return int(getattr(usage, name, 0) or 0)

    return response.text, {
        "prompt_tokens": _count("prompt_token_count"),
        "completion_tokens": _count("candidates_token_count"),
        "total_tokens": _count("total_token_count"),
    }


def generate_response_with_usage(
    system_prompt: str,
    user_message: str,
    provider: str | None = None
) -> dict:
    """Generate an answer and return it with the token usage.

    Returns a dict::

        {"answer": str, "usage": {
            "prompt_tokens": int,
            "completion_tokens": int,
            "total_tokens": int,
        }}

    ``usage`` is taken from the provider's response when available and
    falls back to zeros if the provider did not report usage.
    """

    provider = (
        provider or os.getenv("LLM_PROVIDER", "groq")
    ).lower()

    # GROQ
    if provider == "groq":

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY is missing in Day 06/.env")

        answer, usage = _call_groq(
            system_prompt,
            user_message,
            api_key,
            os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        )

        return {"answer": answer, "usage": usage}

    # GEMINI
    if provider == "gemini":

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing in Day 06/.env")

        answer, usage = _call_gemini(
            system_prompt,
            user_message,
            api_key,
            os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        )

        return {"answer": answer, "usage": usage}

    raise ValueError(
        f"Unsupported provider: {provider}. Choose groq or gemini."
    )


def generate_response(
    system_prompt: str,
    user_message: str,
    provider: str | None = None
) -> str:
    """Generate an answer and return only the text.

    Thin wrapper around :func:`generate_response_with_usage` kept for callers
    that only need the answer string (for example the agent planner).
    """

    return generate_response_with_usage(
        system_prompt,
        user_message,
        provider
    )["answer"]
