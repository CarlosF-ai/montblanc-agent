from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime

SITES = [
    {
        "name": "VVF",
        "search_url": "https://www.vvf-villages.fr/recherche-sejour"
    },
    {
        "name": "VTF",
        "search_url": "https://www.vtf-vacances.com/sejours"
    }
]

DESTINATION = "mont blanc"
START_DATE = "11/07/2026"
END_DATE = "18/07/2026"

ADULTS = 3
CHILDREN = 1

results = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    for site in SITES:

        try:
            print(f"Recherche sur {site['name']}")

            page.goto(site["search_url"], timeout=60000)

            # ⚠️ Les sélecteurs varient selon les sites
            # Ici on tente une logique générique

            page.wait_for_timeout(3000)

            content = page.content().lower()

            if "mont" in content or "chamonix" in content:

                links = page.locator("a").all()

                for link in links:

                    try:
                        text = link.inner_text()
                        href = link.get_attribute("href")

                        if not href:
                            continue

                        if "séjour" in text.lower() or "vacances" in text.lower():

                            if href.startswith("/"):
                                href = site["search_url"] + href

                            results.append({
                                "site": site["name"],
                                "titre": text[:80],
                                "url": href,
                                "periode": f"{START_DATE} → {END_DATE}",
                                "personnes": f"{ADULTS}A + {CHILDREN}E",
                                "date_scan": datetime.now().strftime("%Y-%m-%d %H:%M")
                            })

                    except:
                        pass

        except Exception as e:
            print(e)

    browser.close()

df = pd.DataFrame(results)

df.to_csv("offres.csv", index=False)

print(df)
