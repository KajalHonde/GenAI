
import json
from pathlib import Path

from app.llm import generate_response


# Project folders
BASE_DIR = Path(__file__).resolve().parents[1]
PROMPT_DIR = BASE_DIR / "prompts"
RESULT_FILE = BASE_DIR / "eval" / "results.md"

# Same questions for both prompt versions
questions = [
    ("What should I do during an earthquake?", "earthquake"),
    ("How can I prepare my home for an earthquake?", "earthquake"),
    ("What should I do immediately after an earthquake?", "earthquake"),
    ("What does Drop, Cover and Hold On mean?", "earthquake"),
    ("How can I protect children and elderly people during an earthquake?", "earthquake"),
    ("What should I do during a flood?", "flood"),
    ("Why should people avoid walking through floodwater?", "flood"),
    ("What should I include in a flood emergency kit?", "flood"),
    ("How can I stay safe around electricity during a flood?", "flood"),
    ("What should I do after floodwater recedes?", "flood"),
]

# Prompt A: Basic version
prompt_a = """
You are a disaster management assistant.
Answer disaster-related questions in simple language.
Provide helpful information.
"""

# Prompt B: Your improved AapdaMitra system prompt
prompt_b = (
    PROMPT_DIR / "system_prompt.txt"
).read_text(encoding="utf-8")

# Same output requirements for both versions
json_instruction = """
Return ONLY valid JSON, without Markdown.

{
  "answer": "Your helpful disaster safety answer",
  "confidence": 0.90,
  "follow_up": "A useful follow-up question"
}

Confidence must be a number between 0 and 1.
"""

results = []

for version, base_prompt in [
    ("Prompt A - Basic", prompt_a),
    ("Prompt B - Improved", prompt_b)
]:

    print(f"\nRunning {version}...")

    for number, (question, topic) in enumerate(questions, start=1):

        task_file = PROMPT_DIR / f"{topic}_prompt.txt"
        task_prompt = task_file.read_text(encoding="utf-8")

        complete_prompt = (
            base_prompt
            + "\n\nTASK INSTRUCTIONS:\n"
            + task_prompt
            + "\n\n"
            + json_instruction
        )

        print(f"Question {number}/10: {question}")

        try:
            answer = generate_response(
                system_prompt=complete_prompt,
                user_message=question
            )

            results.append({
                "version": version,
                "number": number,
                "topic": topic,
                "question": question,
                "response": answer
            })

        except Exception as error:
            results.append({
                "version": version,
                "number": number,
                "topic": topic,
                "question": question,
                "response": f"ERROR: {error}"
            })

# Save actual AI responses
with open(RESULT_FILE, "w", encoding="utf-8") as file:

    file.write("# AapdaMitra Prompt Evaluation Results\n\n")

    file.write(
        "Model: openai/gpt-oss-120b\n\n"
    )

    for item in results:

        file.write(f"## {item['version']} - Question {item['number']}\n\n")
        file.write(f"**Topic:** {item['topic']}\n\n")
        file.write(f"**Question:** {item['question']}\n\n")
        file.write("**AI Response:**\n\n")
        file.write(item["response"] + "\n\n")
        file.write("---\n\n")

print("\nEvaluation completed!")
print(f"Results saved to: {RESULT_FILE}")
print(f"Total responses recorded: {len(results)}")
