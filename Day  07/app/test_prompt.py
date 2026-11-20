
from app.context_builder import build_context
from app.prompt import create_prompt
from app.retriever import retrieve_documents


def test_create_prompt_returns_text():
    question = "What should we do during a flood?"

    documents = retrieve_documents(question)
    context = build_context(documents)
    prompt = create_prompt(question, context)

    assert prompt is not None
    assert isinstance(prompt, str)
    assert len(prompt.strip()) > 0


def test_prompt_contains_question():
    question = "What should we do during a flood?"

    documents = retrieve_documents(question)
    context = build_context(documents)
    prompt = create_prompt(question, context)

    assert question in prompt


def test_prompt_contains_context():
    question = "What should we do during a flood?"

    documents = retrieve_documents(question)
    context = build_context(documents)
    prompt = create_prompt(question, context)

    if context.strip():
        assert context in prompt
