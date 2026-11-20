
"""Interactive AapdaMitra Streamlit application.

Run from the project root:
    streamlit run ui/app.py
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

import requests
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
FEEDBACK_FILE = ROOT / "data" / "feedback.jsonl"

st.set_page_config(
    page_title="AapdaMitra | Disaster Safety Assistant",
    page_icon="🛟",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main {background: #f6f8fb;}
    .hero {
        padding: 1.5rem 1.7rem;
        border-radius: 18px;
        background: linear-gradient(115deg, #123b5d, #087e8b);
        color: white;
        margin-bottom: 1rem;
    }
    .hero h1 {color: white; margin: 0;}
    .hero p {color: #e8f5f7; margin-bottom: 0;}
    div.stButton > button {border-radius: 10px; min-height: 2.5rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

CHECKLISTS = {
    "Flood": {
        "Before": [
            "Keep drinking water, dry food, medicines, torch, batteries and first-aid ready.",
            "Keep important documents in a waterproof bag.",
            "Know the nearest safe shelter and evacuation route.",
            "Charge mobile phones and keep a power bank ready.",
            "Move valuables and electrical items to a higher place.",
        ],
        "During": [
            "Move to higher ground when instructed or when water rises.",
            "Never walk, swim or drive through flood water.",
            "Switch off electricity if it is safe to do so.",
            "Keep away from electric poles and fallen wires.",
            "Follow official warnings and rescue instructions.",
        ],
        "After": [
            "Return home only after authorities say it is safe.",
            "Avoid flood water that may contain sewage or chemicals.",
            "Do not switch on wet electrical equipment.",
            "Drink safe or boiled water.",
            "Report damaged roads, buildings and power lines.",
        ],
    },
    "Cyclone": {
        "Before": [
            "Listen to official weather bulletins and evacuation alerts.",
            "Keep an emergency kit, medicines and important documents ready.",
            "Secure loose objects outside the house.",
            "Keep phones charged and emergency contacts available.",
            "Move to a cyclone shelter if instructed.",
        ],
        "During": [
            "Stay indoors, away from windows and glass doors.",
            "Do not go outside during the calm eye of the cyclone.",
            "Turn off electricity and gas if advised and safe.",
            "Stay in the strongest part of the building.",
            "Follow official instructions; do not spread rumours.",
        ],
        "After": [
            "Wait for the official all-clear before going outside.",
            "Stay away from fallen power lines and damaged structures.",
            "Use safe drinking water and hygienic food.",
            "Avoid flooded roads and coastal areas.",
            "Report urgent hazards to local authorities.",
        ],
    },
    "Earthquake": {
        "Before": [
            "Identify safe spots under sturdy tables and away from glass.",
            "Secure shelves, cylinders and heavy furniture.",
            "Keep an emergency kit and shoes near your exit.",
            "Practise Drop, Cover and Hold On with family members.",
            "Know how to turn off gas and electricity safely.",
        ],
        "During": [
            "DROP to the ground, COVER under sturdy furniture and HOLD ON.",
            "Stay indoors until shaking stops; do not use lifts.",
            "Keep away from windows, glass and heavy objects.",
            "If outdoors, move to an open area away from buildings and wires.",
            "If driving, stop in a clear place and stay inside the vehicle.",
        ],
        "After": [
            "Expect aftershocks; be ready to Drop, Cover and Hold On.",
            "Check for injuries and give first aid if trained.",
            "Leave damaged buildings carefully; do not re-enter.",
            "Check for gas leaks and damaged electrical wiring.",
            "Follow official information and avoid damaged areas.",
        ],
    },
    "Heatwave": {
        "Before": [
            "Store drinking water and oral rehydration supplies.",
            "Plan outdoor work for cooler morning or evening hours.",
            "Wear light-coloured, loose-fitting cotton clothes.",
            "Keep an eye on children, older adults and outdoor workers.",
            "Keep rooms shaded and improve ventilation where possible.",
        ],
        "During": [
            "Drink water regularly; do not wait until you feel thirsty.",
            "Stay in shade or a cool indoor place during peak heat.",
            "Avoid strenuous outdoor activity in the afternoon.",
            "Never leave children or pets inside parked vehicles.",
            "If someone is confused or faints in heat, seek urgent medical help.",
        ],
        "After": [
            "Continue drinking water and resting in a cool place.",
            "Seek medical advice if weakness, dizziness or vomiting continues.",
            "Check on neighbours who may need help.",
            "Replace fluids after outdoor work or heavy sweating.",
            "Review the local forecast before planning outdoor activities.",
        ],
    },
    "General": {
        "Before": [
            "Save local emergency numbers and important contacts.",
            "Prepare drinking water, food, medicines and a first-aid kit.",
            "Keep identity documents in a waterproof folder.",
            "Make a family communication and meeting plan.",
            "Know the nearest safe shelter and evacuation route.",
        ],
        "During": [
            "Stay calm and follow verified official instructions.",
            "Move away from immediate danger to a safe location.",
            "Help children, older adults and persons needing assistance.",
            "Keep phone lines free for emergency communication.",
            "Do not forward unverified messages or rumours.",
        ],
        "After": [
            "Check for injuries and contact emergency services if needed.",
            "Avoid damaged buildings, roads and electrical equipment.",
            "Use safe water and maintain hygiene.",
            "Follow local authority updates before returning home.",
            "Help neighbours and report hazards to officials.",
        ],
    },
}

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_approval" not in st.session_state:
    st.session_state.pending_approval = None


def save_feedback(question: str, answer: str, rating: str) -> None:
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "question": question,
        "answer": answer,
        "rating": rating,
    }
    with FEEDBACK_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")


def post_json(base_url: str, endpoint: str, payload: dict):
    url = base_url.rstrip("/") + endpoint
    response = requests.post(url, json=payload, timeout=90)
    response.raise_for_status()
    return response.json()


def show_answer(data: dict) -> str:
    answer = (
        data.get("answer")
        or data.get("response")
        or data.get("message")
        or data.get("output")
        or str(data)
    )
    st.markdown(answer)

    citations = data.get("citations") or data.get("sources") or []
    if citations:
        with st.expander("📚 Sources and citations"):
            for item in citations:
                if isinstance(item, dict):
                    label = (
                        item.get("title")
                        or item.get("source")
                        or item.get("url")
                        or str(item)
                    )
                    url = item.get("url")
                    if url:
                        st.markdown(f"- [{label}]({url})")
                    else:
                        st.write(f"- {label}")
                else:
                    st.write(f"- {item}")

    return answer


with st.sidebar:
    st.title("🛟 AapdaMitra")
    st.caption("Community Disaster Preparedness")

    api_url = st.text_input(
        "FastAPI URL",
        os.getenv("API_URL", "http://127.0.0.1:8000"),
    )

    mode = st.radio(
        "Assistant mode",
        ["Ask (/ask)", "Agent (/agent)"],
    )

    st.divider()
    st.markdown("**Quick safety reminder**")
    st.info(
        "In an emergency, follow local authorities and call the appropriate emergency service."
    )

    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_approval = None
        st.rerun()


st.markdown(
    """
    <div class="hero">
      <h1>🛟 AapdaMitra</h1>
      <p>Your community disaster safety assistant — preparedness, trusted guidance and action checklists.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

overview1, overview2, overview3 = st.columns(3)
overview1.metric("Safety phases", "3", "Before • During • After")
overview2.metric("Hazard guides", str(len(CHECKLISTS)), "Choose your hazard")
overview3.metric("Assistant", "Online UI", "Connects to your FastAPI")

chat_tab, checklist_tab, about_tab = st.tabs(
    ["💬 Chat assistant", "📋 Safety checklist", "ℹ️ About"]
)

with chat_tab:
    st.subheader("Ask AapdaMitra")
    st.caption("Ask a disaster-preparedness question in simple language.")

    quick_cols = st.columns(3)
    quick_questions = [
        "What should I do during an earthquake?",
        "How can I stay safe in a heatwave?",
        "What should I keep in an emergency kit?",
    ]

    for col, question_text in zip(quick_cols, quick_questions):
        if col.button(question_text, use_container_width=True):
            st.session_state.chat_input_value = question_text

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("citations"):
                with st.expander("📚 Sources and citations"):
                    for citation in message["citations"]:
                        st.write(citation)

    question = st.chat_input("Type your disaster-safety question…")

    if "chat_input_value" in st.session_state and not question:
        question = st.session_state.pop("chat_input_value")

    if question:
        st.session_state.messages.append(
            {"role": "user", "content": question}
        )

        with st.chat_message("user"):
            st.markdown(question)

        endpoint = "/ask" if mode.startswith("Ask") else "/agent"
        payload = {"question": question}

        if endpoint == "/agent":
            payload["thread_id"] = "aapdamitra-streamlit"

        with st.chat_message("assistant"):
            try:
                with st.spinner("AapdaMitra is preparing guidance…"):
                    result = post_json(api_url, endpoint, payload)

                answer = show_answer(result)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "citations": (
                            result.get("citations")
                            or result.get("sources")
                            or []
                        ),
                    }
                )

                if (
                    result.get("requires_approval")
                    or result.get("approval_required")
                ):
                    st.session_state.pending_approval = {
                        "question": question,
                        "result": result,
                    }

            except requests.exceptions.ConnectionError:
                st.error(
                    "Cannot connect to FastAPI. Start the backend in another terminal with: "
                    "uvicorn app.main:app --reload"
                )

            except requests.exceptions.HTTPError as exc:
                st.error(f"API error: {exc}")
                if exc.response is not None:
                    st.code(exc.response.text)

            except Exception as exc:  # noqa: BLE001
                st.error(f"Something went wrong: {exc}")

    if st.session_state.pending_approval:
        st.warning(
            "This agent response may need human approval. "
            "Review the API response and use the approval action below if your backend supports it."
        )

        approve_col, reject_col = st.columns(2)

        if approve_col.button("✅ Approve", use_container_width=True):
            st.info(
                "Approval selected. Connect this button to your graph's approval/resume endpoint if your backend exposes one."
            )
            st.session_state.pending_approval = None

        if reject_col.button("❌ Reject", use_container_width=True):
            st.info("Rejection selected.")
            st.session_state.pending_approval = None

    if (
        st.session_state.messages
        and st.session_state.messages[-1]["role"] == "assistant"
    ):
        last_answer = st.session_state.messages[-1]["content"]

        last_question = next(
            (
                message["content"]
                for message in reversed(st.session_state.messages[:-1])
                if message["role"] == "user"
            ),
            "",
        )

        st.divider()
        st.caption("Was this answer helpful?")

        good, bad, _ = st.columns([1, 1, 5])

        if good.button("👍 Helpful"):
            save_feedback(last_question, last_answer, "up")
            st.success("Thank you — feedback saved.")

        if bad.button("👎 Not helpful"):
            save_feedback(last_question, last_answer, "down")
            st.success("Thank you — feedback saved.")


with checklist_tab:
    st.subheader("Village safety notice-board checklist")
    st.write(
        "Choose a hazard, tick the actions completed, and print or download the checklist."
    )

    hazard = st.selectbox(
        "Choose hazard",
        list(CHECKLISTS.keys()),
    )

    phase_tabs = st.tabs(
        ["🟢 Before", "🟠 During", "🔵 After"]
    )

    for phase, phase_tab in zip(
        ["Before", "During", "After"],
        phase_tabs,
    ):
        with phase_tab:
            items = CHECKLISTS[hazard][phase]

            st.markdown(f"**{hazard} — {phase} the event**")

            completed = 0

            for item_no, item in enumerate(items):
                key = f"{hazard}_{phase}_{item_no}"
                checked = st.checkbox(item, key=key)
                completed += int(checked)

            st.progress(completed / len(items))
            st.caption(
                f"{completed} of {len(items)} actions completed"
            )

    printable = [
        f"<h2>{hazard} Safety Checklist</h2>",
        "<p>Tick each action after completing it.</p>",
    ]

    for phase in ["Before", "During", "After"]:
        printable.append(f"<h3>{phase}</h3><ul>")

        for item_no, item in enumerate(CHECKLISTS[hazard][phase]):
            key = f"{hazard}_{phase}_{item_no}"
            mark = "☑" if st.session_state.get(key, False) else "☐"
            printable.append(f"<li>{mark} {item}</li>")

        printable.append("</ul>")

    printable.append(
        "<p><small>AapdaMitra | Follow official local instructions.</small></p>"
    )

    html = """
    <!doctype html>
    <html>
    <head>
    <meta charset="utf-8">
    <title>AapdaMitra Safety Checklist</title>
    <style>
    body {
        font-family: Arial, sans-serif;
        max-width: 850px;
        margin: 35px auto;
        line-height: 1.6;
        color: #183044;
    }
    h2 {
        border-bottom: 3px solid #087e8b;
        padding-bottom: 8px;
    }
    li { margin: 9px 0; }
    @media print {
        button { display: none; }
    }
    </style>
    </head>
    <body>
    """ + "\n".join(printable) + """
    <button onclick="window.print()">Print checklist</button>
    </body>
    </html>
    """

    st.download_button(
        "⬇️ Download printable checklist (HTML)",
        data=html,
        file_name=f"aapdamitra_{hazard.lower()}_checklist.html",
        mime="text/html",
        use_container_width=True,
    )

    st.caption(
        "Open the downloaded HTML file in a browser and select Print."
    )


with about_tab:
    st.subheader("About AapdaMitra")

    st.write(
        "AapdaMitra is a community disaster-preparedness assistant. "
        "It connects a Streamlit interface to the project's FastAPI knowledge and agent endpoints."
    )

    st.markdown(
        """
        **Features**

        - Ask questions through the `/ask` endpoint or use the `/agent` endpoint.
        - Display source citations when the API returns them.
        - Save thumbs-up and thumbs-down feedback locally.
        - Use a three-phase Before / During / After checklist for common hazards.
        - Download a checklist that can be printed for a village notice board.
        """
    )

    st.warning(
        "This tool is for preparedness information and does not replace emergency services or official instructions."
    )
