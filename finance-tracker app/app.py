import os
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from datetime import date
from dotenv import load_dotenv

from db import init_db, add_expense, read_expenses, delete_expense
from ai import categorize_expense, saving_tips

# Load local .env (no effect on Streamlit Cloud)
load_dotenv()

st.set_page_config(page_title="Finance Tracker", page_icon="💰", layout="wide")

# --- Init DB once per session
if "db_init" not in st.session_state:
    init_db()
    st.session_state.db_init = True

st.title("💰 Personal Finance Tracker (AI-assisted)")

with st.sidebar:
    st.header("Add Expense")
    d = st.date_input("Date", value=date.today())
    desc = st.text_input("Description", placeholder="e.g. Uber to office")
    amt = st.number_input("Amount (₹)", min_value=0.0,
                          step=50.0, format="%.2f")
    pay = st.selectbox("Payment Method", [
                       "Card", "UPI", "Cash", "NetBanking", "Other"], index=1)
    auto_cat = st.checkbox("AI categorize", value=True)
    manual_cat = st.selectbox(
        "Manual Category (used if AI off)",
        ["Food", "Transport", "Utilities", "Housing", "Healthcare", "Entertainment",
         "Shopping", "Education", "Bills", "Other"],
        index=0
    )

    if st.button("➕ Add"):
        if not desc or amt <= 0:
            st.error("Please enter a valid description and amount.")
        else:
            cat = categorize_expense(desc) if auto_cat else manual_cat
            add_expense(d, desc, cat, amt, pay)
            st.success(f"Added ({cat}).")
            st.experimental_rerun()

    st.divider()
    st.header("Import CSV")
    up = st.file_uploader(
        "Upload bank CSV (date,description,amount,payment_method)", type=["csv"])
    if up:
        try:
            df = pd.read_csv(up)
            required = {"date", "description", "amount"}
            if not required.issubset(set(map(str.lower, df.columns))):
                st.error("CSV must include columns: date, description, amount")
            else:
                # Normalize columns
                cols = {c: c.lower() for c in df.columns}
                df.rename(columns=cols, inplace=True)
                df["payment_method"] = df.get("payment_method", "Other")
                with st.spinner("Categorizing & importing..."):
                    for _, r in df.iterrows():
                        cat = categorize_expense(str(r["description"]))
                        add_expense(r["date"], str(r["description"]), cat, float(
                            r["amount"]), str(r["payment_method"]))
                st.success("Import complete.")
                st.experimental_rerun()
        except Exception as e:
            st.error(f"Import failed: {e}")

# --- Data view
rows = read_expenses()
df = pd.DataFrame(rows, columns=[
                  "id", "date", "description", "category", "amount", "payment_method"])

col1, col2 = st.columns([2, 1], gap="large")

with col1:
    st.subheader("Transactions")
    if df.empty:
        st.info("No expenses yet. Add one from the sidebar.")
    else:
        # Filters
        f1, f2, f3 = st.columns(3)
        with f1:
            cats = st.multiselect("Filter Categories", sorted(
                df["category"].unique().tolist()))
        with f2:
            pm = st.multiselect("Payment Methods", sorted(
                df["payment_method"].unique().tolist()))
        with f3:
            rng = st.date_input("Date Range", [])
        fdf = df.copy()
        if cats:
            fdf = fdf[fdf["category"].isin(cats)]
        if pm:
            fdf = fdf[fdf["payment_method"].isin(pm)]
        if len(rng) == 2:
            fdf = fdf[(fdf["date"] >= str(rng[0])) &
                      (fdf["date"] <= str(rng[1]))]

        st.dataframe(
            fdf.drop(columns=["id"]).reset_index(drop=True),
            use_container_width=True,
            hide_index=True
        )

        # Delete action
        if not df.empty:
            del_id = st.number_input(
                "Delete by Row ID", min_value=0, step=1, value=0)
            if st.button("🗑️ Delete"):
                if del_id in df["id"].values:
                    delete_expense(int(del_id))
                    st.success(f"Deleted row {int(del_id)}.")
                    st.experimental_rerun()
                else:
                    st.error("Invalid ID.")

with col2:
    st.subheader("Spending by Category")
    if not df.empty:
        sum_by_cat = df.groupby("category")[
            "amount"].sum().sort_values(ascending=False)
        fig, ax = plt.subplots()
        sum_by_cat.plot(kind="bar", ax=ax)
        ax.set_ylabel("Amount (₹)")
        ax.set_xlabel("")
        ax.set_title("Total Spend")
        st.pyplot(fig, use_container_width=True)

        st.subheader("AI Saving Tips")
        tips = saving_tips(sum_by_cat.to_dict())
        st.info(tips)
    else:
        st.caption("Charts and tips appear after you add expenses.")
