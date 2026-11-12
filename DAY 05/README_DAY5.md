# AapdaMitra - Day 5 files

## Where to put these files

Copy the contents into your existing AapdaMitra project root. Keep your existing project files. If you already have a `main.py`, do not overwrite it without checking it first; merge the four example endpoints into your existing FastAPI app or ask for help integrating them.

Expected structure:

```text
AapdaMitra/
├── main.py
├── requirements.txt
├── README_DAY5.md
├── docs/
│   └── how_llms_work.md
└── data/
    └── user_questions.json
```

## Run

Open VS Code terminal in the project root:

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Open these addresses in your browser:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/questions
- http://127.0.0.1:8000/questions/q6

## Explain one function

`home()` is called when a user sends a GET request to `/`. The function returns a JSON message. `@app.get("/")` connects the URL route to the Python function.

## Git checkpoint

After confirming your own project works, run:

```bash
git status
git add .
git commit -m "Day 5: LLM documentation and questions"
git tag checkpoint-1
git tag
```

If the tag must be uploaded to GitHub:

```bash
git push origin checkpoint-1
```

## Important note about the questions

These are realistic sample disaster-related questions. The `user_questions.json` file records all ten. Q6 is intentionally unanswerable from a static sample dataset because live bridge status is not included. The sample FastAPI endpoint returns a safe limitation message; it does not check a real bridge or live emergency feed.

Replace these proposed questions with the six exact questions from your original project card if your instructor expects those exact six.
