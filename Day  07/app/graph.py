
import re
from typing import TypedDict, Optional

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt

from app.tools import heat_risk_index
from app.rag import answer_question
from app.llm import generate_response


# 1. Define agent state and memory
class AgentState(TypedDict):
    question: str
    decision: Optional[str]
    temperature: Optional[float]
    humidity: Optional[float]
    result: Optional[dict]
    approved: Optional[bool]


# 2. Planner prompt
PLANNER_PROMPT = """
You are the planner for AapdaMitra disaster safety agent.

Choose the required tool:

HEAT = heat calculation
RAG = disaster safety information
BOTH = heat calculation and safety information

Examples:
Calculate heat risk at 40 degrees C and 60% humidity.
Answer: HEAT

How can people stay safe during a cyclone?
Answer: RAG

Calculate heat risk and explain heatwave safety precautions.
Answer: BOTH

Return only HEAT, RAG, or BOTH.
"""


# 3. Planner node
def planner_node(state: AgentState):

    response = generate_response(
        system_prompt=PLANNER_PROMPT,
        user_message=state["question"]
    )

    response = response.strip().upper()

    match = re.search(r"\b(BOTH|HEAT|RAG)\b", response)

    if match:
        decision = match.group(1)
    else:
        decision = "RAG"

    return {"decision": decision}


# 4. Human approval node
def approval_node(state: AgentState):

    approved = interrupt({
        "message": "Please approve execution of the selected tools.",
        "question": state["question"],
        "selected_tools": state["decision"]
    })

    return {"approved": bool(approved)}


# 5. Prepare a focused RAG question
def build_rag_question(question: str, decision: str):

    if decision != "BOTH":
        return question

    question_lower = question.lower()

    heat_keywords = [
        "heat",
        "temperature",
        "humidity",
        "heatwave",
        "heat wave"
    ]

    if any(word in question_lower for word in heat_keywords):
        return (
            "What safety precautions should people follow "
            "during a heatwave?"
        )

    return question


# 6. Execute selected tools
def execute_node(state: AgentState):

    question = state["question"]
    decision = state["decision"]

    result = {}

    # Execute heat calculation
    if decision in ["HEAT", "BOTH"]:

        temperature = state.get("temperature")
        humidity = state.get("humidity")

        if temperature is None or humidity is None:

            result["heat_risk"] = (
                "Please provide temperature in Celsius "
                "and humidity in percentage."
            )

        else:

            result["heat_risk"] = heat_risk_index(
                temperature,
                humidity
            )

    # Execute RAG search
    if decision in ["RAG", "BOTH"]:

        rag_question = build_rag_question(
            question,
            decision
        )

        result["safety_information"] = answer_question(
            rag_question
        )

    return {"result": result}


# 7. Approval router
def approval_router(state: AgentState):

    if state.get("approved"):
        return "execute"

    return "end"


# 8. Build LangGraph
builder = StateGraph(AgentState)

builder.add_node("planner", planner_node)
builder.add_node("approval", approval_node)
builder.add_node("execute", execute_node)

builder.add_edge(START, "planner")
builder.add_edge("planner", "approval")

builder.add_conditional_edges(
    "approval",
    approval_router,
    {
        "execute": "execute",
        "end": END
    }
)

builder.add_edge("execute", END)


# 9. Add memory
memory = MemorySaver()

graph = builder.compile(
    checkpointer=memory
)


# 10. Run agent
def run_agent(
    question: str,
    temperature: Optional[float] = None,
    humidity: Optional[float] = None,
    thread_id: str = "aapdamitra-user"
):

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    initial_state = {
        "question": question,
        "decision": None,
        "temperature": temperature,
        "humidity": humidity,
        "result": None,
        "approved": None
    }

    return graph.invoke(
        initial_state,
        config=config
    )


# 11. Direct testing
if __name__ == "__main__":

    response = run_agent(
        question=(
            "Calculate heat risk at 40 degrees C "
            "and 60% humidity, and explain safety precautions."
        ),
        temperature=40,
        humidity=60
    )

    print("\nAapdaMitra LangGraph Response:")
    print(response)
