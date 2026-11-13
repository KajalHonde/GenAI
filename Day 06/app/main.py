
import json
import re
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.llm import generate_response


# --------------------------------
# 1. Project Configuration
# --------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_DIR = BASE_DIR / "prompts"

app = FastAPI(
    title="AapdaMitra API",
    description="GenAI Disaster Management Assistant",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# --------------------------------
# 2. Request Model
# --------------------------------

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    topic: str = "general"


# --------------------------------
# 3. Load Prompt Files
# --------------------------------

def load_prompt(filename: str) -> str:

    prompt_path = PROMPT_DIR / filename

    if not prompt_path.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Prompt file not found: {filename}"
        )

    return prompt_path.read_text(encoding="utf-8")


def build_system_prompt(topic: str) -> str:

    allowed_topics = {
        "general": None,
        "earthquake": "earthquake_prompt.txt",
        "flood": "flood_prompt.txt"
    }

    topic = topic.lower().strip()

    if topic not in allowed_topics:
        raise HTTPException(
            status_code=400,
            detail="Topic must be general, earthquake or flood."
        )

    system_prompt = load_prompt("system_prompt.txt")

    task_filename = allowed_topics[topic]

    if task_filename:
        task_prompt = load_prompt(task_filename)
        system_prompt += "\n\nTASK-SPECIFIC INSTRUCTIONS:\n" + task_prompt

    return system_prompt


# --------------------------------
# 4. Parse AI JSON Response
# --------------------------------

def parse_ai_response(ai_text: str) -> dict:

    try:
        # Remove Markdown code fences if present
        cleaned = re.sub(
            r"^```(?:json)?\s*|\s*```$",
            "",
            ai_text.strip(),
            flags=re.IGNORECASE
        )

        data = json.loads(cleaned)

        answer = data.get("answer")
        confidence = data.get("confidence")
        follow_up = data.get("follow_up")

        if not isinstance(answer, str) or not answer.strip():
            raise ValueError("Missing answer")

        if isinstance(confidence, bool) or not isinstance(
            confidence, (int, float)
        ):
            raise ValueError("Confidence must be a number")

        if not 0 <= confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")

        if not isinstance(follow_up, str):
            raise ValueError("Follow_up must be a string")

        return {
            "answer": answer,
            "confidence": float(confidence),
            "follow_up": follow_up
        }

    except (json.JSONDecodeError, ValueError, AttributeError):
        raise HTTPException(
            status_code=502,
            detail="AI returned an invalid JSON response."
        )


# --------------------------------
# 5. Home Endpoint
# --------------------------------

@app.get("/")
def home():

    return {
        "message": "Welcome to AapdaMitra API",
        "status": "running"
    }


# --------------------------------
# 6. Health Endpoint
# --------------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "AapdaMitra API"
    }


# --------------------------------
# 7. Chat Endpoint
# --------------------------------

@app.post("/chat")
def chat(request: ChatRequest):

    try:

        # Load system and task prompts
        system_prompt = build_system_prompt(request.topic)

        # Ask AI to return JSON
        json_instruction = """
        IMPORTANT:
        Return ONLY a valid JSON object.
        Do not use Markdown or code fences.

        Required JSON format:
        {
            "answer": "Your disaster safety answer",
            "confidence": 0.90,
            "follow_up": "A useful follow-up question"
        }

        Confidence must be a number between 0 and 1.
        """

        complete_prompt = system_prompt + "\n\n" + json_instruction

        # Call Groq or Gemini through llm.py
        ai_response = generate_response(
            system_prompt=complete_prompt,
            user_message=request.message
        )

        # Convert AI response into structured JSON
        result = parse_ai_response(ai_response)

        return result

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"AI service error: {str(e)}"
        )
