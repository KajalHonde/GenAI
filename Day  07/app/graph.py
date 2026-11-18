
from typing import TypedDict, Optional

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

from app.tools import heat_risk_index
from app.rag import answer_question
from app.llm import generate_response


# 1. Define agent memory/state
class AgentState(TypedDict):

    question: str
    decision: Optional[str]
    temperature: Optional[float]
    humidity: Optional[float]
    result: Optional[dict]
    approved: Optional[bool]


# 2. LLM planner
PLANNER_PROMPT = """
You are the planner for AapdaMitra disaster safety agent.

Choose the required tool:

HEAT = heat calculation
RAG = disaster safety information
BOTH = heat calculation and safety information

Return only HEAT, RAG, or BOTH.
"""


def planner_node(state: AgentState):

    response = generate_response(
        system_prompt=PLANNER_PROMPT,
        user_message=state["question"]
    )

    decision = response.strip().upper()

    if "BOTH" in decision:
        decision = "BOTH"
    elif "HEAT" in decision:
        decision = "HEAT"
    else:
        decision = "RAG"

    return {"decision": decision}


# 3. Human approval node
def approval_node(state: AgentState):

    approved = interrupt({
        "message": "Please approve execution of the selected tools.",
        "question": state["question"],
        "selected_tools": state["decision"]
    })

    return {"approved": bool(approved)}


# 4. Execute selected tools
def execute_node(state: AgentState):

    question = state["question"]
    decision = state["decision"]

    result = {}

    if decision in ["HEAT", "BOTH"]:

        temperature = state.get("temperature")
        humidity = state.get("humidity")

        if temperature is None or humidity is None:

            result["heat_risk"] = (
                "Please provide temperature in °C "
                "and humidity in %."
            )

        else:

            result["heat_risk"] = heat_risk_index(
                temperature,
                humidity
            )

    if decision in ["RAG", "BOTH"]:

        result["safety_information"] = answer_question(
            question
        )

    return {"result": result}


# 5. Check approval
def approval_router(state: AgentState):

    if state.get("approved"):
        return "execute"

    return "end"


# 6. Build LangGraph
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


# 7. Add memory
memory = MemorySaver()

graph = builder.compile(
    checkpointer=memory
)


# 8. Run agent
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


if __name__ == "__main__":

    response = run_agent(
        question="Calculate heat risk and explain precautions.",
        temperature=40,
        humidity=60
    )

    print("\nAapdaMitra LangGraph Response:")
    print(response)
