def score_offer(price, has_pension, location_match):

    score = 0

    # 💰 prix
    if price:
        if price < 2000:
            score += 40
        elif price < 2500:
            score += 25
        elif price < 3000:
            score += 10

    # 🍽️ pension complète
    if has_pension:
        score += 30

    # 🏔️ localisation
    if location_match:
        score += 30

    if score >= 80:
        return "🔥 EXCELLENTE OFFRE"
    elif score >= 50:
        return "👍 BONNE OFFRE"
    else:
        return "❌ MOYEN"
