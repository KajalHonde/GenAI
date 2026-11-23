# AapdaMitra — Interview Preparation

**Kajal Santosh Honde**
Project: AapdaMitra — Disaster Safety Assistant

---

## 60-Second Pitch

> Practise saying this aloud before Demo Day. Time yourself — aim for 55–60 seconds.

---

Hi, I am Kajal. I built AapdaMitra, which means "disaster friend" in Hindi.

The problem I solved is real. A Gram Panchayat member in a village near the
Godavari River, Kopargaon, needs reliable guidance for monsoon floods and the
April–May heatwave. Official NDMA material exists, but it is spread across long
PDFs written for officials and terse web pages written for citizens. Generic
chatbots fill that gap by inventing safety steps — which can be dangerous.

AapdaMitra answers citizen questions from retrieved NDMA content, cites its
sources, and says "I don't know" when the data cannot answer. It never invents
forecasts or safety instructions.

The core pipeline is: HTML ingestion → word-level chunking → MiniLM embeddings →
ChromaDB vector store → FastAPI RAG service, with a system prompt that forbids
fabrication. On top of that I built a LangGraph agent with a custom heat-index
tool, a Streamlit chat UI with a printable Before / During / After checklist for
the village notice board, 39 pytest tests, CI, Docker Compose, and a live Render
deployment.

The hardest problem was getting the retrieval to serve the right level of
advice — do's and don'ts for families, guidelines for officials — without ever
claiming to have live warnings. I will explain exactly how I solved that.

---

## The Hardest Problem (Interview Story)

**Problem statement**

The source material is two very different kinds of text. The citizen-facing pages
(`flood_dos_donts.html`, `ndma_home.html`) are short, action-oriented, and use
simple language: *"Do not walk through moving water."* The guidelines PDF is
long, technical, and written for district officials: multi-page policy sections
that rarely appear in a family's question.

If retrieval treats both sources the same, a question like *"What should my
family do before a flood?"* retrieves guideline policy paragraphs instead of the
plain do's and don'ts, and the LLM rewrites them as if they were family advice —
inventing phrasing and sometimes inventing safety steps the source never contained.

The second failure mode was forecasts. A question like *"Will it flood tomorrow
near Kopargaon?"* has no answer in the data. Early builds answered it anyway by
mixing retrieved context with LLM hallucination.

**What I tried first (and why it failed)**

I chunked all documents at a fixed size (100 words) with no distinction by
source type. At distance threshold 0.55, the RAG returned a mix of citizen and
guideline chunks for every question. The LLM blended them into an answer that
sounded authoritative but contained fabricated specifics.

I tried raising the cosine-distance threshold to 0.45. That reduced hallucination
but also dropped recall — the assistant said "I don't know" too often for
questions it should have been able to answer.

**The solution I arrived at**

Three changes together fixed both failure modes:

1. **Source-aware system prompt.** The system prompt explicitly tells the LLM:
   *"Answer using only the supplied context. Never invent facts or safety
   instructions. Never invent citations."* The key phrase is "only the supplied
   context" — the LLM is not permitted to reach outside it.

2. **Distance threshold as an abstention gate.** I kept the threshold at 0.55
   but added a second gate: if no chunk passes the threshold, the function
   returns the fixed string *"I don't know."* without calling the LLM at all.
   This is in `app/rag.py` (`MAX_DISTANCE = 0.55`, the `_abstain()` path).
   That means a forecast question — which produces no close semantic match in
   advisory-only data — never reaches the LLM and cannot hallucinate an answer.

3. **Keyword-based citation filter.** Citations are only attached when the
   retrieved chunk's section title shares keywords with the question. This means
   a guideline-sourced chunk that happens to rank highly will not be cited as
   family advice — the user sees only sources whose topic genuinely matches what
   they asked.

**What I measured**

I ran a 15-question eval set (`eval/eval_set.json`). Q6 is the abstention test:
*"What is the personal mobile number of the local disaster officer in my
village?"* — something the data can never answer. Both configurations (chunk
size 100 / top-k 3, and chunk size 150 / top-k 5) pass Q6 with the correct
"I don't know." response. The overall retrieval score is 60% (9/15) on keyword
recall; the abstention behaviour, the citation accuracy, and the absence of
fabricated safety steps are the parts I value most.

**What I would do next with more time**

Separate the sources at index time by tagging each chunk with an audience field
(`citizen` or `official`). At query time, classify the question's audience and
boost chunks with the matching tag in a re-ranking step. That would raise recall
for citizen questions without exposing official policy text to families.

---

## 10 Likely Interview Questions and Answers

---

### Q1 — What is AapdaMitra and who is it for?

AapdaMitra is a retrieval-augmented disaster-safety assistant for village
families in India, particularly near the Godavari River. The primary user I
designed for is a Gram Panchayat member who needs plain-language guidance about
floods, heatwaves and earthquakes — before, during and after — to share with
their community.

It answers questions from NDMA official sources, cites those sources, and
refuses to answer when the data cannot support it. It is not a live warning
system; it is a preparedness and awareness tool.

---

### Q2 — Explain the RAG pipeline from document to answer.

1. **Ingest**: NDMA HTML pages (`flood_dos_donts.html`, `ndma_home.html`,
   `earthquake.html`, `ndma_guidelines.html`) are parsed with BeautifulSoup,
   preserving section headings as chunk titles (`app/chunking.py`).

2. **Chunk**: Each document is split into 100-word overlapping windows (overlap
   20 words) so context is not lost at chunk boundaries.

3. **Embed**: Each chunk is embedded with `sentence-transformers/all-MiniLM-L6-v2`
   — a lightweight 384-dim model that runs locally without an API key
   (`app/embed.py`).

4. **Store**: Chunks are stored in a persistent ChromaDB collection with cosine
   distance (`app/vectorstore.py`).

5. **Retrieve**: At query time the question is embedded with the same model and
   the top-k nearest chunks are returned. Any chunk with distance > 0.55 is
   discarded (`app/rag.py`).

6. **Generate**: The surviving chunks are formatted into a context block and
   sent to the LLM (Groq or Gemini) with a strict system prompt that forbids
   fabrication. Token usage is recorded.

7. **Return**: The answer, citations, and question are returned to the caller.
   The result is cached so an identical question is answered from memory.

---

### Q3 — Why use ChromaDB instead of a hosted vector database?

Two reasons. First, Chroma runs in-process with no external service, which means
the development loop is fast — no network, no API key, no billing. Second, for
the free Render tier, adding a hosted vector DB adds cost and cold-start
complexity. The trade-off is that the index is not durable across Render
restarts; the app rebuilds it on first startup by running `index_documents.py`.
If I scaled this to a production service I would switch to a hosted store such
as Pinecone or Weaviate and persist the index separately.

---

### Q4 — What is the LangGraph agent doing that plain RAG cannot?

Plain RAG always takes the same path: retrieve → generate. The LangGraph agent
adds two things.

First, **tool selection**: a planner LLM reads the question and chooses between
RAG retrieval, the `heat_risk_index` calculator (a pure-Python Rothfusz
regression that computes "feels like" temperature from air temperature and
relative humidity), or both. A question like *"Calculate heat risk at 40 °C and
60% humidity and explain safety precautions"* needs a numeric tool, not just
document retrieval.

Second, **human-in-the-loop approval**: the graph interrupts before running any
tool and waits for explicit approval from the caller (`/agent` returns
`approval_required`). The caller sends a second request with `approval: true`
to resume. This is implemented with LangGraph's `interrupt` and `MemorySaver`
checkpointer (`app/graph.py`).

---

### Q5 — How does your system prevent hallucination?

Three complementary layers:

1. **System prompt constraint**: The LLM is instructed to answer only from the
   supplied context and never to invent facts, safety instructions, or citations.

2. **Abstention gate**: If no retrieved chunk passes the cosine-distance
   threshold (0.55), the function returns "I don't know." without calling the
   LLM at all. No model tokens are spent and no hallucination is possible.

3. **Prompt-injection guard**: Requests that try to override these rules — such
   as *"ignore previous instructions"* — are refused by a pattern check before
   the input ever reaches the model (`app/observability.py`, `is_prompt_injection`).

None of these is perfect. A sufficiently confusing prompt that doesn't match
injection patterns could still cause the LLM to deviate. The right next step
is an LLM-based classifier that evaluates the answer against the retrieved
context before returning it.

---

### Q6 — Walk me through the production hardening you added on Day 13.

Four things in `app/observability.py`:

- **Latency and token logging**: every request to `/ask`, `/search/semantic` and
  `/agent` records wall-clock latency and (for `/ask`) prompt plus completion
  tokens from the provider's usage object. Aggregates are served at `GET /metrics`.

- **Answer cache**: an in-memory LRU store (128 entries, 10-minute TTL) keyed on
  the normalised question and top-k value. In the benchmark, a repeat question
  returned in 0.2 ms with 0 tokens versus ~2.6 s and 1259 tokens cold — roughly
  13,000× faster and free.

- **Input limits**: questions are capped at 500 characters, search queries at 200
  characters. Over-length input returns HTTP 422 before any processing begins.

- **Prompt-injection guard**: 18 known attack phrases are matched with a compiled
  regex. A blocked request returns a fixed refusal, records a `blocked` metric,
  and spends no tokens.

---

### Q7 — What would you change to serve 10,000 users a day?

Right now the cache and metrics store are in-process Python dicts — they reset on
restart and are not shared across workers. For real scale I would:

1. Move the cache to Redis with a TTL so it survives restarts and is shared
   across multiple API workers.
2. Push metrics to a time-series store (Prometheus + Grafana) instead of an
   in-memory deque.
3. Move the ChromaDB index to a persistent hosted vector store.
4. Add rate limiting per IP address at the API gateway layer.
5. Run the embedding model as a separate microservice so the API workers do not
   block on inference during heavy load.

---

### Q8 — How did you evaluate the RAG quality?

I built a 15-question evaluation set (`eval/eval_set.json`) covering earthquake
preparedness, flood safety, and an intentional abstention question (Q6: asking
for a local officer's phone number — something the data can never answer).

For Q1–Q5 and Q7–Q15, the evaluator checks whether any expected keyword appears
in the retrieved text. For Q6, it checks that the LLM returns exactly "I don't
know." — anything else is a hallucination failure.

I ran two configurations: chunk size 100 / top-k 3 (Config A) and chunk size
150 / top-k 5 (Config B). Both scored 9/15 on keyword recall and both passed Q6.
Config A is the winner because it uses fewer tokens per request (smaller chunks
mean shorter context windows).

The evaluation script (`eval/run_eval.py`) runs both configs, prints the per-
question pass/fail, and updates the README table automatically.

---

### Q9 — What is the Before / During / After checklist feature and why does it matter?

The Streamlit UI (`ui/app.py`) has a three-tab checklist for five hazards: Flood,
Cyclone, Earthquake, Heatwave, and General. Each tab lists five actionable steps.
The user can tick each item and then download a printable HTML file.

The reason it matters for the target user — a Gram Panchayat member — is that
they often prepare physical notice boards for the village. A digital assistant is
useful for answering questions, but a printed, ticked checklist is what they can
pin to the wall, hand to families, or read at a community meeting. It converts
the AI's output into a usable offline artefact.

---

### Q10 — What is one failure you encountered and how did you measured and fixed it?

**Failure**: the Render deployment was returning a red ❌ for every push, even
when CI was green.

**Root cause I found**: `app/llm.py` hard-coded a path
`Path(__file__).parents[2] / "Day 06" / ".env"`. Inside Docker that resolves to
`/Day 06/.env` — a path that does not exist in the container. `load_dotenv`
silently failed, so `GROQ_API_KEY` was never set, and the first LLM call
crashed the worker.

**How I measured it**: The GitHub Deployments tab showed "Failed to deploy" on
every commit, and the Render dashboard logs showed
`ValueError: GROQ_API_KEY is missing`. I reproduced it locally by running the
Docker container without a `.env` file and confirming the same error.

**Fix**: Changed `llm.py` to call `load_dotenv()` with no arguments first
(which picks up `.env` from the working directory when running locally), then
tries the sibling path only if the file actually exists. On Render, the platform
injects env vars directly, so `load_dotenv` is correctly a no-op. I also added
`envVars` to `render.yaml` for the non-secret defaults and added `.env.example`
documenting every required key.

---

## Demo Day Checklist (run through this twice before presenting)

**Setup — do this 15 minutes before the demo starts**

- [ ] Open the live Render API: `https://aapdamitra-api.onrender.com/health`
      and wait for `{"status": "ok"}` (may take 30 s to wake)
- [ ] Open the live Render UI: `https://aapdamitra-ui.onrender.com`
- [ ] Open the interactive docs: `https://aapdamitra-api.onrender.com/docs`
- [ ] Open this repository on GitHub so the README and code are visible
- [ ] Have the PROGRESS.md open to show every item is closed

**Demo flow — 5 minutes**

1. **(30 s) Intro**: Say your 60-second pitch. Point at the README architecture
   diagram.

2. **(60 s) Live RAG**: In the Streamlit UI, ask:
   *"What should I do before a flood?"*
   Show the answer, the citations, and the source links.

3. **(30 s) Abstention**: Ask:
   *"What is the personal mobile number of the local disaster officer?"*
   Show "I don't know." — explain that the data has advice, not live contacts.

4. **(45 s) Checklist**: Switch to the Safety Checklist tab, choose Flood,
   tick a few Before items, click Download and show the printable HTML.

5. **(30 s) API docs**: Open `/docs`, expand `POST /ask`, run it live in the
   browser.

6. **(30 s) Production metrics**: Open `/metrics`, show total_requests,
   avg_latency_ms, and cache_hit_rate.

7. **(45 s) Hardest problem**: Tell the retrieval / abstention story
   (see Interview Story section above). Point at `app/rag.py` lines
   `MAX_DISTANCE = 0.55` and the `_abstain()` function.

**Q&A — 3 minutes**

Use the answers in the 10 questions section above. If you do not know an
answer, say: *"I would start by measuring X and then try Y."* That is a better
answer than guessing.
