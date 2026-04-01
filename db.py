import sqlite3
from pathlib import Path

DB_PATH = Path("expenses.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    payment_method TEXT
);
"""


def get_conn():
    # Streamlit runs the script multiple times; use a lightweight connection each time
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute(SCHEMA)
        conn.commit()


def add_expense(date, description, category, amount, payment_method):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO expenses(date, description, category, amount, payment_method) VALUES (?, ?, ?, ?, ?)",
            (str(date), description, category, float(
                amount), payment_method or None),
        )
        conn.commit()


def read_expenses():
    with get_conn() as conn:
        return conn.execute(
            "SELECT id, date, description, category, amount, payment_method FROM expenses ORDER BY date DESC, id DESC"
        ).fetchall()


def delete_expense(row_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM expenses WHERE id = ?", (row_id,))
        conn.commit()
