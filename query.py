"""
query.py — Grounded Generation
Retrieves chunks (retrieve.py) and feeds them to Groq's llama-3.3-70b-versatile
with a system prompt that forces answers from the retrieved context only.

Source attribution is guaranteed programmatically: sources are collected from the
retrieved chunks' metadata, not parsed out of the model's free-text answer.

Public entry point: ask(question) -> {"answer": str, "sources": list[str]}
"""

import os
from dotenv import load_dotenv
from groq import Groq

from retrieve import retrieve

load_dotenv()

MODEL = "llama-3.3-70b-versatile"
TOP_K = 5
NO_INFO = "I don't have enough information on that."

_client = None


def _get_client() -> Groq:
    """Lazy-init the Groq client so importing this module never requires a key."""
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key or api_key == "your_key_here":
            raise RuntimeError(
                "GROQ_API_KEY is not set. Copy .env.example to .env and add your "
                "free key from https://console.groq.com"
            )
        _client = Groq(api_key=api_key)
    return _client


SYSTEM_PROMPT = (
    "You are the Unofficial UCI Professor Guide. You answer questions about UCI "
    "ICS/CS professors and courses using ONLY the numbered context passages provided "
    "in the user message.\n\n"
    "STRICT RULES:\n"
    "1. Use ONLY information found in the provided context passages. Do NOT use any "
    "prior knowledge about these professors, courses, or universities.\n"
    "2. If the context does not contain enough information to answer the question, "
    f'reply with EXACTLY this sentence and nothing else: "{NO_INFO}"\n'
    "3. Do not guess, infer beyond the text, or add general advice that is not "
    "supported by the passages.\n"
    "4. When you state a fact, it must be traceable to one of the passages.\n"
    "Answer concisely in 2-5 sentences."
)


def _build_context(chunks: list[dict]) -> str:
    """Render retrieved chunks as numbered passages with their source labels."""
    blocks = []
    for i, c in enumerate(chunks, 1):
        blocks.append(
            f"[Passage {i} | Source: {c['source']} | Professor: {c['professor']}]\n"
            f"{c['text']}"
        )
    return "\n\n".join(blocks)


def ask(question: str, top_k: int = TOP_K) -> dict:
    """
    End-to-end grounded answer.
    Returns {"answer": str, "sources": list[str]}.
    Sources are derived from retrieved chunks, not from the model's text.
    """
    chunks = retrieve(question, top_k=top_k)

    if not chunks:
        return {"answer": NO_INFO, "sources": []}

    context = _build_context(chunks)
    user_message = (
        f"Context passages:\n\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer using only the passages above."
    )

    response = _get_client().chat.completions.create(
        model=MODEL,
        temperature=0.0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )
    answer = response.choices[0].message.content.strip()

    # Programmatic source attribution: unique sources, order preserved by rank.
    # If the model declined to answer, surface no sources to avoid false attribution.
    if answer == NO_INFO:
        sources = []
    else:
        seen = set()
        sources = []
        for c in chunks:
            if c["source"] not in seen:
                seen.add(c["source"])
                sources.append(c["source"])

    return {"answer": answer, "sources": sources}


if __name__ == "__main__":
    TEST_QUERIES = [
        "Does Thornton curve ICS 33?",
        "Is Wong Ma worth taking even though he is hard?",
        # A question the documents do not cover — should decline.
        "What is the parking situation at UCI?",
    ]
    for q in TEST_QUERIES:
        result = ask(q)
        print(f"\n{'='*65}\nQ: {q}\n{'-'*65}")
        print(f"A: {result['answer']}")
        print(f"Sources: {', '.join(result['sources']) or '(none)'}")
