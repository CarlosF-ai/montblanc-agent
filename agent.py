from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
from scorer import score_offer

SITES = [
    {"name": "VVF", "url": "https://www.vvf-villages.fr"},
    {"name": "VTF", "url": "https://www.vtf-vacances.com"},
    {"name": "Miléade", "url": "https://www.mileade.com"},
]

KEYWORDS = ["mont", "chamonix", "haute-savoie"]

results = []

def extract_price(text):

    numbers = []

    for w in text.split():
        w = w.replace("€", "").replace(",", "")
        if w.isdigit():
            v = int(w)
            if 100 < v < 6000:
                numbers.append(v)

    return min(numbers) if numbers else None


with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    for s in SITES:

        try:
            page.goto(s["url"], timeout=60000)
            page.wait_for_timeout(3000)

            text = page.content().lower()

            location_match = any(k in text for k in KEYWORDS)

            price = extract_price(page.inner_text("body"))

            has_pension = "pension" in text

            offer_score = score_offer(price, has_pension, location_match)

            results.append({
                "site": s["name"],
                "url": s["url"],
                "price": price if price else "N/A",
                "pension": has_pension,
                "score": offer_score,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            })

        except Exception as e:
            print(e)

    browser.close()

df = pd.DataFrame(results)

df.to_csv("offers.csv", index=False)

print(df)
