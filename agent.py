from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import os

SEARCH_URLS = [
    {
        "name": "VVF",
        "url": "https://www.vvf-villages.fr"
    },
    {
        "name": "VTF",
        "url": "https://www.vtf-vacances.com"
    },
    {
        "name": "Miléade",
        "url": "https://www.mileade.com"
    }
]

KEYWORDS = [
    "mont blanc",
    "chamonix",
    "pension complète",
    "pension complete"
]

MAX_PRICE = 2500

results = []

def send_email(content):

    sender = os.environ["EMAIL_USER"]
    password = os.environ["EMAIL_PASSWORD"]
    receiver = os.environ["EMAIL_TO"]

    msg = MIMEText(content)

    msg["Subject"] = "🏔️ Nouvelle promo Mont-Blanc"
    msg["From"] = sender
    msg["To"] = receiver

    smtp = smtplib.SMTP_SSL("smtp.gmail.com", 465)

    smtp.login(sender, password)

    smtp.send_message(msg)

    smtp.quit()

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    for site in SEARCH_URLS:

        try:

            print(f"Analyse {site['name']}")

            page.goto(site["url"], timeout=60000)

            content = page.content().lower()

            matched = False

            for keyword in KEYWORDS:
                if keyword in content:
                    matched = True

            if matched:

                prices = []

                text = page.locator("body").inner_text()

                words = text.split()

                for word in words:

                    clean = (
                        word.replace("€", "")
                        .replace(",", "")
                        .replace(".", "")
                    )

                    if clean.isdigit():

                        value = int(clean)

                        if 100 < value < 5000:
                            prices.append(value)

                if prices:

                    best_price = min(prices)

                    score = "⭐"

                    if best_price < 2000:
                        score = "⭐⭐⭐"
                    elif best_price < 2300:
                        score = "⭐⭐"

                    results.append({
                        "site": site["name"],
                        "url": site["url"],
                        "prix": best_price,
                        "score": score,
                        "date": datetime.now().strftime("%d/%m/%Y %H:%M")
                    })

                    page.screenshot(
                        path=f"{site['name']}.png",
                        full_page=True
                    )

        except Exception as e:
            print(e)

    browser.close()

if results:

    df = pd.DataFrame(results)

    df.to_csv(
        "offres.csv",
        mode="a",
        index=False,
        header=not os.path.exists("offres.csv")
    )

    good_deals = df[df["prix"] <= MAX_PRICE]

    if not good_deals.empty:

        message = f"""

Promotions détectées :

{good_deals.to_string(index=False)}

Critères :
- Mont-Blanc
- Pension complète
- 3 adultes
- 1 adolescent 15 ans
- 11 → 18 juillet

"""

        send_email(message)

        print("Email envoyé")

    else:
        print("Aucune bonne affaire")

else:
    print("Aucun résultat")