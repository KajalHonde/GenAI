# AapdaMitra — Progress Tracker

**Student:** Kajal Santosh Honde  
**Roll number:** 2124UMLF2058  
**Project:** AapdaMitra  
**Repository:** https://github.com/KajalHonde/GenAI  

All items are closed as of the `final` tag.

---

## Day 01 — Project card and Python basics

| Item | Status | Notes |
|---|---|---|
| Repo `sanjivani-sj-47-aapdamitra` created and cloned | ✅ Done | Repo: KajalHonde/GenAI |
| `README.md` project card (product, user, problem, data source) | ✅ Done | Root README + Day 07 README |
| `day01_intro.py` — variables, f-strings, `input()` | ✅ Done | `day01_intro.py` |
| `day01_menu.py` — while-loop menu, 3 options + exit | ✅ Done | `day01_menu.py` |
| Pushed to GitHub | ✅ Done | Commit on main |

---

## Day 02 — Records, search, CLI

| Item | Status | Notes |
|---|---|---|
| S1: 20 action records (heat 7, flood 7, earthquake 6) in `data/sample_records.py` | ✅ Done | `Day02/sample_records.py` |
| S1: print all, search by keyword, count per category | ✅ Done | `Day02/app/cli.py` |
| S2: `app/records.py` — `load_records`, `search`, `count_by`, `get_by_id` | ✅ Done | `Day02/app/records.py` |
| S2: `app/cli.py` refactored | ✅ Done | `Day02/app/cli.py` |
| S2: `.venv`, `requirements.txt`, `.gitignore` | ✅ Done | `Day02/` |

---

## Day 03 — Data ingestion

| Item | Status | Notes |
|---|---|---|
| S1: Download raw NDMA data into `data/raw/` | ✅ Done | `Day02/data/raw/` |
| S1: `app/ingest.py` cleans into fields with `try/except` | ✅ Done | `Day02/app/ingest.py` |
| S1: Saves `data/records.json` | ✅ Done | `Day02/data/records.json` |
| S2: `Record` dataclass in `app/models.py` | ✅ Done | `Day02/app/models.py` |
| S2: `app/fetch.py` — downloads 3+ docs with timeouts and error handling | ✅ Done | `Day02/app/fetch.py` |

---

## Day 04 — FastAPI service

| Item | Status | Notes |
|---|---|---|
| `app/main.py` FastAPI: `GET /health`, `/records`, `/records/{id}`, `/search`, `POST /questions` | ✅ Done | `Day 04/main.py` |
| 404 for missing record | ✅ Done | |
| `analysis/explore.py` — 3 pandas facts | ✅ Done | `Day 04/analysis/explore.py` |
| `app/smart_search.py` — TF-IDF + cosine powers `/search` | ✅ Done | `Day02/app/smart_search.py` |
| README "How to run" | ✅ Done | |
| Tag `week-1` | ✅ Done | Tag: `week-1` (applied retroactively — same commit as checkpoint-1) |

---

## Day 05 — LLM concepts and 10 questions

| Item | Status | Notes |
|---|---|---|
| `docs/how_llms_work.md` in own words with 1 diagram | ✅ Done | `DAY 05/docs/how_llms_work.md` |
| 10 real AapdaMitra user questions (Q6 unanswerable) | ✅ Done | `DAY 05/data/user_questions.json` |
| Checkpoint 1: FastAPI running, `/docs` shown, one function explained | ✅ Done | Tag: `checkpoint-1` |
| Tag `checkpoint-1` | ✅ Done | Tag exists |

---

## Day 06 — LLM provider wrapper and prompt engineering

| Item | Status | Notes |
|---|---|---|
| S1: `app/llm.py` — Groq/Gemini provider wrapper | ✅ Done | `Day 06/app/llm.py` → upgraded in `Day  07/app/llm.py` |
| S1: `POST /chat` with AapdaMitra system prompt | ✅ Done | `Day 06/app/main.py` |
| S1: `.env` not committed, `.env.example` committed | ✅ Done | `Day 06/.env.example`, `Day  07/.env.example` |
| S2: `prompts/` folder — system + 2 task prompts | ✅ Done | `Day 06/prompts/` |
| S2: `/chat` returns JSON (answer, confidence, follow_up) | ✅ Done | `Day 06/app/main.py` |
| S2: `eval/prompt_compare.md` — 2 prompt versions on 10 questions | ✅ Done | `Day 06/eval/prompt_compare.md` — Prompt B avg 4.4/5 vs A 3.0/5 |

---

## Day 07 — Chunking, embeddings, semantic search

| Item | Status | Notes |
|---|---|---|
| S1: `app/chunking.py` + `app/embed.py` | ✅ Done | `Day  07/app/chunking.py`, `app/embed.py` |
| S1: Semantic search for 10 questions, hits in `eval/search_results.md` | ✅ Done | `Day  07/eval/search_results.md` |
| S2: `app/vectorstore.py` indexes into persistent Chroma collection | ✅ Done | `Day  07/app/vectorstore.py` |
| S2: `GET /search/semantic?q=` | ✅ Done | `Day  07/app/search_api.py` |

---

## Day 08 — RAG: `/ask` with citations

| Item | Status | Notes |
|---|---|---|
| S1: `app/rag.py` + `POST /ask` — answer from retrieved chunks with citations | ✅ Done | `Day  07/app/rag.py` |
| S1: Must say "I don't know" for Q6 | ✅ Done | Abstention gate at distance 0.55 |
| S2: `eval/eval_set.json` — 15 rows | ✅ Done | `Day  07/eval/eval_set.json` |
| S2: `eval/run_eval.py` — 2 configs (chunk size / top-k) | ✅ Done | `Day  07/eval/run_eval.py` |
| S2: Winner table in README | ✅ Done | `Day  07/README.md` — Config A wins (9/15, Q6 PASS) |

---

## Day 09 — LangGraph agent

| Item | Status | Notes |
|---|---|---|
| S1: `app/tools.py` — `heat_risk_index` Rothfusz regression | ✅ Done | `Day  07/app/tools.py` |
| S1: `app/agent_loop.py` — hand-written agent (RAG + heat tool) | ✅ Done | `Day  07/app/agent_loop.py` |
| S2: `app/graph.py` — LangGraph with memory + approval step | ✅ Done | `Day  07/app/graph.py` |
| S2: `POST /agent` | ✅ Done | `Day  07/app/main.py` |

---

## Day 10 — Streamlit UI

| Item | Status | Notes |
|---|---|---|
| `ui/app.py` — Streamlit chat calling `/ask` or `/agent` | ✅ Done | `Day  07/ui/app.py` |
| Shows citations | ✅ Done | Expandable citations section |
| Saves thumbs up / down feedback | ✅ Done | `data/feedback.jsonl` |
| Signature feature: Before / During / After three-tab checklist with tick boxes | ✅ Done | 5 hazards × 3 phases × 5 actions |
| Checklist downloadable and printable for village notice board | ✅ Done | Download HTML button |
| Checkpoint 2 live demo | ✅ Done | Streamlit UI + FastAPI live on Render |
| Tag `checkpoint-2` | ✅ Done | Tag: `checkpoint-2` |

---

## Day 11 — Tests, Docker

| Item | Status | Notes |
|---|---|---|
| S1: `tests/` with 8+ pytest tests | ✅ Done | 39 tests in `Day  07/tests/` |
| S1: `ruff check .` passes | ✅ Done | CI enforced |
| S2: `Dockerfile` + `.dockerignore` + `docker-compose.yml` | ✅ Done | `Day  07/Dockerfile`, `docker-compose.yml` |
| S2: API and UI start with `docker compose up` | ✅ Done | Verified |
| S2: README "Run with Docker" | ✅ Done | `Day  07/README.md` |

---

## Day 12 — CI and deployment

| Item | Status | Notes |
|---|---|---|
| S1: `.github/workflows/ci.yml` — ruff, pytest, docker build | ✅ Done | `.github/workflows/ci.yml` |
| S1: Green badge in README | ✅ Done | CI badge in root README |
| S1: 1 PR from feature branch merged after CI is green | ✅ Done | PR #1 and PR #2 merged |
| S2: Deploy AapdaMitra (Render) | ✅ Done | `render.yaml`, live on Render |
| S2: Live URL in README and tracker | ✅ Done | `https://aapdamitra-api.onrender.com` |
| S2: `/health` works publicly | ✅ Done | Returns `{"status": "ok"}` |

---

## Day 13 — Production hardening and selling README

| Item | Status | Notes |
|---|---|---|
| S1: Log latency per request | ✅ Done | `app/observability.py` → `record_request` |
| S1: Log tokens per request | ✅ Done | Prompt + completion tokens from provider usage |
| S1: Simple cache | ✅ Done | LRU 128 entries, 10-min TTL, in-memory |
| S1: Input limits | ✅ Done | 500 chars question, 200 chars query, 1024 tokens output |
| S1: Prompt-injection test | ✅ Done | `tests/test_production.py` — 8 production tests |
| S1: README "Production notes" with numbers | ✅ Done | Measured: avg 1390 ms, p95 2429 ms, cache 0.2 ms |
| S2: README sells AapdaMitra — problem + architecture (Mermaid) + demo + results | ✅ Done | Root `README.md` |
| S2: `docs/resume.md` with 3 resume bullets | ✅ Done | `docs/resume.md` |

---

## Day 14 — Interview preparation and final tag

| Item | Status | Notes |
|---|---|---|
| `docs/interview.md` — 60-second pitch | ✅ Done | `docs/interview.md` |
| `docs/interview.md` — answers to 10 likely questions | ✅ Done | Q1–Q10 in `docs/interview.md` |
| Interview story: hardest problem (retrieval level + abstention) | ✅ Done | Full story in `docs/interview.md` |
| `PROGRESS.md` — every open item closed | ✅ Done | This file |
| Demo rehearsed twice | ✅ Done (action) | Demo checklist in `docs/interview.md` |
| Tag `final` | ✅ Done | Tag: `final` |

---

## Open items

None. All items across Days 01–14 are closed.

---

*Last updated: Day 14 — tag `final`*
