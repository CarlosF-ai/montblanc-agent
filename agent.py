from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import os

SITES = [
    {"name": "VVF", "url": "https://www.vvf-villages.fr"},
    {"name": "VTF", "url": "https://www.vtf-vacances.com"},
    {"name": "Miléade", "url": "https://www.mileade.com"},
]

KEYWORDS = ["mont blanc", "chamonix", "pension"]

data = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    for s in SITES:
        try:
            page.goto(s["url"], timeout=60000)
            text = page.content().lower()

            if any(k in text for k in KEYWORDS):

                prices = []

                for t in page.inner_text("body").split():
                    clean = t.replace("€", "").replace(",", "")
                    if clean.isdigit():
                        v = int(clean)
                        if 100 < v < 5000:
                            prices.append(v)

                if prices:
                    data.append({
                        "site": s["name"],
                        "prix": min(prices),
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                    })

        except:
            pass

    browser.close()

df_new = pd.DataFrame(data)

file = "offres.csv"

if os.path.exists(file):
    df_old = pd.read_csv(file)
    df = pd.concat([df_old, df_new], ignore_index=True)
else:
    df = df_new

df.to_csv(file, index=False)

print(df)
