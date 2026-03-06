def calculate_lead_score(data):
    score = 0

    # Intent
    if data["intent"].lower() == "buyer":
        score += 30
    elif data["intent"].lower() == "seller":
        score += 25
    elif data["intent"].lower() == "investor":
        score += 20

    # Budget
    budget = data.get("budget", 0)
    if budget and budget > 500000:
        score += 30
    elif budget and budget > 300000:
        score += 20
    elif budget and budget > 150000:
        score += 10

    # Timeline
    timeline = data.get("timeline", "").lower()
    if timeline == "immediate":
        score += 30
    elif timeline == "1-3 months":
        score += 20
    elif timeline == "6+ months":
        score += 5

    # Priority
    if score >= 70:
        priority = "Hot"
    elif score >= 40:
        priority = "Warm"
    else:
        priority = "Cold"

    return score, priority