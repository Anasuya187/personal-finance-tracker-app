

ALLOWED = ["Food", "Transport", "Utilities", "Housing", "Healthcare",
           "Entertainment", "Shopping", "Education", "Bills", "Other"]


def categorize_expense(description: str) -> str:
    desc = description.lower()

    if any(x in desc for x in ["food", "restaurant", "zomato", "swiggy"]):
        return "Food"
    elif any(x in desc for x in ["uber", "ola", "bus", "train", "petrol"]):
        return "Transport"
    elif any(x in desc for x in ["electricity", "water", "gas"]):
        return "Utilities"
    elif any(x in desc for x in ["rent", "house"]):
        return "Housing"
    elif any(x in desc for x in ["hospital", "medicine", "doctor"]):
        return "Healthcare"
    elif any(x in desc for x in ["movie", "netflix"]):
        return "Entertainment"
    elif any(x in desc for x in ["amazon", "shopping", "flipkart"]):
        return "Shopping"
    elif any(x in desc for x in ["school", "course", "fees"]):
        return "Education"
    elif any(x in desc for x in ["bill", "recharge"]):
        return "Bills"
    else:
        return "Other"


def saving_tips(summary: dict) -> str:
    if not summary:
        return "No data yet."

    tips = []

    if summary.get("Food", 0) > 3000:
        tips.append("Reduce food delivery expenses.")
    if summary.get("Transport", 0) > 2000:
        tips.append("Try public transport to save money.")
    if summary.get("Shopping", 0) > 4000:
        tips.append("Limit unnecessary shopping.")

    if not tips:
        return "Your spending looks balanced. Good job!"

    return "\n".join(f"• {t}" for t in tips)