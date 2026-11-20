import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from groq import Groq

# Load .env file from Day 06 folder
BASE_DIR = Path(__file__).resolve().parents[2] / "Day 06"
load_dotenv(BASE_DIR / ".env")


def generate_response(
    system_prompt: str,
    user_message: str,
    provider: str | None = None
) -> str:

    provider = (
        provider or os.getenv("LLM_PROVIDER", "groq")
    ).lower()

    # GROQ
    if provider == "groq":

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY is missing in Day 06/.env")

        client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            model=os.getenv(
                "GROQ_MODEL",
                "openai/gpt-oss-120b"
            ),
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

        return response.choices[0].message.content or ""

    # GEMINI
    elif provider == "gemini":

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing in Day 06/.env")

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=os.getenv(
                "GEMINI_MODEL",
                "gemini-2.5-flash"
            ),
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.3,
                max_output_tokens=1024
            )
        )

        if not response.text:
            raise ValueError("Gemini returned an empty response.")

        return response.text

    else:
        raise ValueError(
            f"Unsupported provider: {provider}. Choose groq or gemini."
        )