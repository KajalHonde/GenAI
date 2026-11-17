
import re

from app.tools import heat_risk_index
from app.rag import answer_question
from app.llm import generate_response


PLANNER_PROMPT = """
You are the decision-making planner for AapdaMitra,
a disaster safety AI agent.

Choose which tool is required for the user's question.

Available tools:

1. HEAT
Use when the user asks for heat risk, heat index,
feels-like temperature, or a heat calculation.

2. RAG
Use when the user asks about disaster information,
precautions, safety instructions, floods, earthquakes,
cyclones, tsunamis, landslides, or heat-wave precautions.

3. BOTH
Use when the user needs a heat calculation AND
additional disaster safety information.

Examples:

Question: Calculate heat risk at 40°C and 60% humidity.
Answer: HEAT

Question: How can people stay safe during a cyclone?
Answer: RAG

Question: Calculate heat risk at 40°C and explain safety precautions.
Answer: BOTH

Return ONLY one word:
HEAT, RAG, or BOTH.
"""


def extract_heat_values(question):
    """Extract temperature and humidity."""

    temperature = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:°\s*C|degrees?\s*C|celsius)",
        question,
        re.IGNORECASE
    )

    humidity = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:%|percent)",
        question,
        re.IGNORECASE
    )

    if temperature and humidity:
        return (
            float(temperature.group(1)),
            float(humidity.group(1))
        )

    return None


def rule_based_fallback(question):
    """Fallback if the LLM planner fails."""

    question = question.lower()

    heat_keywords = [
        "heat risk",
        "heat index",
        "feels like",
        "temperature",
        "humidity"
    ]

    safety_keywords = [
        "precaution",
        "safety",
        "stay safe",
        "protect",
        "what should people do",
        "how can people"
    ]

    needs_heat = any(
        word in question for word in heat_keywords
    )

    needs_safety = any(
        word in question for word in safety_keywords
    )

    if needs_heat and needs_safety:
        return "BOTH"

    if needs_heat:
        return "HEAT"

    return "RAG"


def plan_tools(question):
    """Ask the LLM to select the required tools."""

    try:

        decision = generate_response(
            system_prompt=PLANNER_PROMPT,
            user_message=f"User question: {question}"
        )

        decision = decision.strip().upper()

        # Accept only the three supported decisions.
        match = re.search(r"\b(HEAT|RAG|BOTH)\b", decision)

        if match:
            return match.group(1)

        return rule_based_fallback(question)

    except Exception as error:

        print("Planner unavailable. Using fallback:", error)

        return rule_based_fallback(question)


def agent_loop(question):

    print("\nAapdaMitra Agent Started")

    # Step 1: Ask the LLM to select tools.
    decision = plan_tools(question)

    print("Planner Decision:", decision)

    # Step 2: Execute the heat tool.
    if decision == "HEAT":

        values = extract_heat_values(question)

        if values is None:
            return {
                "tool_used": "none",
                "result": "Please provide temperature in °C and humidity in %."
            }

        temperature, humidity = values

        result = heat_risk_index(
            temperature,
            humidity
        )

        return {
            "tool_used": "heat_risk_index",
            "result": result
        }

    # Step 3: Execute the RAG tool.
    if decision == "RAG":

        result = answer_question(question)

        return {
            "tool_used": "rag_search",
            "result": result
        }

    # Step 4: Execute both tools.
    if decision == "BOTH":

        values = extract_heat_values(question)

        if values is None:

            return {
                "tool_used": "rag_search",
                "result": {
                    "safety_information": answer_question(question),
                    "missing_information": (
                        "Please provide temperature in °C "
                        "and humidity in % to calculate heat risk."
                    )
                }
            }

        temperature, humidity = values

        heat_result = heat_risk_index(
            temperature,
            humidity
        )

        rag_result = answer_question(question)

        return {
            "tool_used": [
                "heat_risk_index",
                "rag_search"
            ],
            "result": {
                "heat_risk": heat_result,
                "safety_information": rag_result
            }
        }


if __name__ == "__main__":

    question = input("Ask AapdaMitra: ")

    response = agent_loop(question)

    print("\nAgent Response:")
    print(response)
