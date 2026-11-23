
"""Interactive AapdaMitra Streamlit application.

Run from the project root:
    streamlit run ui/app.py
"""
from __future__ import annotations

import datetime
import json
import os
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
    """Save feedback to the API (persists server-side) and also locally."""
    # Always write locally as a backup.
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "question": question,
        "answer": answer,
        "rating": rating,
    }
    with FEEDBACK_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")

    # Also POST to the API so it's readable from /feedback.
    try:
        api_url = os.getenv("API_URL", "http://127.0.0.1:8000")
        headers = {}
        secret = os.getenv("API_SECRET_KEY", "")
        if secret:
            headers["X-API-Key"] = secret
        requests.post(
            api_url.rstrip("/") + "/feedback",
            json=record,
            headers=headers,
            timeout=10,
        )
    except Exception:  # noqa: BLE001, S110
        pass  # Never crash the UI over a failed feedback POST


def post_json(base_url: str, endpoint: str, payload: dict):
    url = base_url.rstrip("/") + endpoint
    headers = {}
    secret = os.getenv("API_SECRET_KEY", "")
    if secret:
        headers["X-API-Key"] = secret
    response = requests.post(url, json=payload, headers=headers, timeout=90)
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

# ---------------------------------------------------------------------------
# NOVELTY: Village Risk Dashboard — Kopargaon, Maharashtra
# Shows live seasonal risk, heat index calculator and quick-action bar.
# No other disaster chatbot does this for a specific village in real-time.
# ---------------------------------------------------------------------------
_now = datetime.datetime.now()
_month = _now.month
_day = _now.day

# --- Seasonal risk levels for Godavari basin, Kopargaon area ---
# Flood: monsoon June-Sep peak; Heat: April-May peak
def _flood_risk(month: int) -> tuple[str, str, str]:
    if month in (7, 8):
        return "🔴 HIGH", "red", "Peak monsoon — Godavari in spate. Villages on flood plain on alert."
    if month in (6, 9):
        return "🟠 MEDIUM", "orange", "Monsoon active. Monitor river levels daily."
    if month in (10,):
        return "🟡 LOW-MED", "orange", "Post-monsoon. Waterlogging and landslides possible."
    return "🟢 LOW", "green", "Dry season. Good time to prepare emergency kits."

def _heat_risk_level(month: int) -> tuple[str, str, str]:
    if month in (4, 5):
        return "🔴 HIGH", "red", "Peak heatwave season. Limit outdoor work 11am–4pm."
    if month in (3, 6):
        return "🟠 MEDIUM", "orange", "Rising temperatures. Keep water and ORS ready."
    if month in (11, 12, 1, 2):
        return "🟢 LOW", "green", "Cool season. Normal precautions sufficient."
    return "🟡 LOW-MED", "orange", "Moderate heat. Drink water regularly."

def _days_until(target_month: int, target_day: int = 1) -> int:
    target = datetime.date(_now.year, target_month, target_day)
    if target < _now.date():
        target = datetime.date(_now.year + 1, target_month, target_day)
    return (target - _now.date()).days

flood_level, flood_color, flood_msg = _flood_risk(_month)
heat_level, heat_color, heat_msg = _heat_risk_level(_month)

st.markdown("### 🌍 Kopargaon Village Risk Dashboard")
st.caption(f"Godavari basin, Maharashtra — updated {_now.strftime('%d %b %Y')}")

dash_col1, dash_col2, dash_col3 = st.columns(3)

with dash_col1:
    st.markdown(
        f"""
        <div style='background:#1e1e2e;padding:16px;border-radius:12px;border-left:5px solid {flood_color}'>
        <b style='font-size:1.1rem'>🌊 Flood Risk</b><br>
        <span style='font-size:1.5rem;font-weight:bold;color:{flood_color}'>{flood_level}</span><br>
        <small>{flood_msg}</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

with dash_col2:
    st.markdown(
        f"""
        <div style='background:#1e1e2e;padding:16px;border-radius:12px;border-left:5px solid {heat_color}'>
        <b style='font-size:1.1rem'>🌡️ Heat Risk</b><br>
        <span style='font-size:1.5rem;font-weight:bold;color:{heat_color}'>{heat_level}</span><br>
        <small>{heat_msg}</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

with dash_col3:
    days_flood = _days_until(6)
    days_heat = _days_until(4)
    next_event = ("Flood season", days_flood) if days_flood < days_heat else ("Peak heat", days_heat)
    st.markdown(
        f"""
        <div style='background:#1e1e2e;padding:16px;border-radius:12px;border-left:5px solid #888'>
        <b style='font-size:1.1rem'>📅 Next Alert Season</b><br>
        <span style='font-size:1.5rem;font-weight:bold;color:#aaa'>{next_event[1]} days</span><br>
        <small>Until {next_event[0]} begins</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# --- Heat Index Calculator (inline, no chatbot needed) ---
with st.expander("🌡️ Heat Index Calculator — check if today is dangerous", expanded=False):
    st.caption("Enter today's conditions near Kopargaon to get the 'feels like' temperature instantly.")
    hi_col1, hi_col2, hi_col3 = st.columns([1, 1, 2])
    with hi_col1:
        temp_input = st.number_input("Air temperature (°C)", min_value=20, max_value=55, value=38, step=1)
    with hi_col2:
        hum_input = st.number_input("Humidity (%)", min_value=10, max_value=100, value=60, step=5)
    with hi_col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Calculate risk", use_container_width=True):
            try:
                from app.tools import heat_risk_index
                result = heat_risk_index(float(temp_input), float(hum_input))
                risk = result["risk_level"]
                feels = result["feels_like_c"]
                advice = result["advice"]
                color_map = {"caution": "🟡", "extreme caution": "🟠", "danger": "🔴"}
                icon = color_map.get(risk, "⚪")
                st.success(
                    f"{icon} Feels like **{feels}°C** — **{risk.upper()}**\n\n{advice}"
                )
            except Exception as e:  # noqa: BLE001
                st.error(f"Calculation error: {e}")

# --- Quick Action Bar ---
st.markdown("**⚡ Quick Actions**")
qa_cols = st.columns(4)
quick_actions = [
    ("🌊 Flood prep", "What should a family do before a flood to prepare their home?"),
    ("🌡️ Heatwave safety", "How can we protect elderly people during a heatwave?"),
    ("🏔️ Earthquake drill", "What is Drop Cover and Hold On and when should we do it?"),
    ("🎒 Emergency kit", "What items should every family keep in a disaster emergency kit?"),
]
for col, (label, question) in zip(qa_cols, quick_actions):
    if col.button(label, use_container_width=True):
        st.session_state["dashboard_question"] = question
        st.rerun()

st.divider()

chat_tab, checklist_tab, feedback_tab, about_tab = st.tabs(
    ["💬 Chat assistant", "📋 Safety checklist", "📊 Feedback", "ℹ️ About"]
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

    # Pick up questions fired from the dashboard quick-action bar.
    if "dashboard_question" in st.session_state and not question:
        question = st.session_state.pop("dashboard_question")

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


with feedback_tab:
    st.subheader("User Feedback")
    st.caption("See what your friends thought about AapdaMitra's answers.")

    api_url_fb = os.getenv("API_URL", "http://127.0.0.1:8000")
    secret_fb = os.getenv("API_SECRET_KEY", "")
    headers_fb = {"X-API-Key": secret_fb} if secret_fb else {}

    try:
        resp = requests.get(
            api_url_fb.rstrip("/") + "/feedback",
            headers=headers_fb,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total responses", data["total"])
        col2.metric("👍 Helpful", data["thumbs_up"])
        col3.metric("👎 Not helpful", data["thumbs_down"])

        if data["total"] > 0:
            st.divider()

            filter_opt = st.radio(
                "Show",
                ["All", "👍 Helpful only", "👎 Not helpful only"],
                horizontal=True,
            )

            records = data["records"]
            if filter_opt == "👍 Helpful only":
                records = [r for r in records if r["rating"] == "up"]
            elif filter_opt == "👎 Not helpful only":
                records = [r for r in records if r["rating"] == "down"]

            for record in reversed(records):
                icon = "👍" if record["rating"] == "up" else "👎"
                with st.expander(
                    f"{icon} {record['timestamp']} — {record['question'][:60]}..."
                    if len(record["question"]) > 60
                    else f"{icon} {record['timestamp']} — {record['question']}"
                ):
                    st.markdown(f"**Question:** {record['question']}")
                    st.markdown(f"**Answer:** {record['answer']}")
                    st.markdown(f"**Rating:** {icon}")
        else:
            st.info(
                "No feedback yet. Share the app with friends and ask them "
                "to rate answers with 👍 or 👎."
            )

    except Exception as exc:  # noqa: BLE001
        st.warning(f"Could not load feedback: {exc}")


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
