import os
from openai import OpenAI

ALLOWED = ["Food", "Transport", "Utilities", "Housing", "Healthcare",
           "Entertainment", "Shopping", "Education", "Bills", "Other"]


def _client():
    # Works locally with .env and on Streamlit Cloud with Secrets
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # Streamlit Cloud exposes secrets via env; locally use python-dotenv in app.py
        raise RuntimeError("OPENAI_API_KEY not set")
    return OpenAI(api_key=api_key)


def categorize_expense(description: str) -> str:
    client = _client()
    sys = ("You are an expense categorizer. "
           f"Return ONLY one of: {', '.join(ALLOWED)}.")
    msg = f"Expense: {description}\nCategory:"
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": sys},
                  {"role": "user", "content": msg}],
        temperature=0
    )
    cat = (res.choices[0].message.content or "").strip()
    # sanitize
    return cat if cat in ALLOWED else "Other"


def saving_tips(summary: dict) -> str:
    """summary is like {'Food': 1234.0, 'Transport': 567.0, ...}"""
    client = _client()
    sys = ("You analyze monthly spending and give concise, practical tips. "
           "Use bullet points. Avoid generic advice; be specific to the data.")
    msg = f"Monthly spend by category (INR): {summary}. Provide 3-5 tips."
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": sys},
                  {"role": "user", "content": msg}],
        temperature=0.4
    )
    return (res.choices[0].message.content or "").strip()
