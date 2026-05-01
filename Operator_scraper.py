# operator_scraper.py
# FragTrack - Siege.gg Yearly Operator Data Scraper
# Scrapes most picked attack and defense operators per player per year

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

# ─── Years To Scrape ──────────────────────────────────────────────────────────
YEARS = [2020, 2021, 2022, 2023, 2024, 2025, 2026]

# ─── Setup Chrome Driver ──────────────────────────────────────────────────────
def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver

def parse_operators(html, year):
    """
    Extracts each player's most picked attack and defense
    operator, plus their rating and KD for that year.
    """
    soup = BeautifulSoup(html, "html.parser")
    records = []

    rows = soup.find_all("tr", role="row")

    for row in rows:
        try:
            # Player name
            name_tag = row.find("td", class_="sp__player position-relative")
            if not name_tag:
                continue
            name = name_tag.find("a").text.strip()

            # Rating
            rating_tag = row.find("td", class_=lambda c: c and "sp__rating" in c)
            rating = float(rating_tag.text.strip()) if rating_tag else None

            # KD
            kd_tag = row.find("td", class_="sp__kd")
            kd = kd_tag.text.strip() if kd_tag else None

            # Attack operator
            atk_td = row.find("td", class_=lambda c: c and "sp__atk" in c)
            atk_operator = None
            if atk_td:
                atk_img = atk_td.find("img", class_=lambda c: c and "op__icon" in c)
                if atk_img:
                    atk_operator = atk_img.get("title", "").strip()

            # Defense operator
            def_td = row.find("td", class_=lambda c: c and "sp__def" in c)
            def_operator = None
            if def_td:
                def_img = def_td.find("img", class_=lambda c: c and "op__icon" in c)
                if def_img:
                    def_operator = def_img.get("title", "").strip()

            if atk_operator or def_operator:
                records.append({
                    "year": year,
                    "player": name,
                    "rating": rating,
                    "kd": kd,
                    "top_atk_operator": atk_operator,
                    "top_def_operator": def_operator
                })

        except Exception as e:
            print(f"  Skipping row: {e}")
            continue

    return records

# ─── Save To CSV ──────────────────────────────────────────────────────────────
def save_to_csv(records, filename="data/operator_data.csv"):
    os.makedirs("data", exist_ok=True)
    df = pd.DataFrame(records)
    df.to_csv(filename, index=False)
    print(f"\n  Saved {len(records)} records to {filename}")

# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  FragTrack Operator Scraper - Siege.gg")
    print("=" * 50)

    driver = create_driver()
    all_records = []

    for year in YEARS:
        url = f"https://siege.gg/years/{year}"
        print(f"\nScraping year: {year}")
        try:
            driver.get(url)

            # Wait for player table to load
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "tr[role='row']"))
            )

            # Wait for operator icons to render
            time.sleep(4)

            html = driver.page_source
            records = parse_operators(html, year)
            print(f"  Found {len(records)} player records for {year}")
            all_records.extend(records)

            time.sleep(3)

        except Exception as e:
            print(f"  Error scraping {year}: {e}")
            continue

    driver.quit()

    if all_records:
        save_to_csv(all_records)
        print("\nOperator scraping complete!")
        print(f"Total records: {len(all_records)}")
    else:
        print("\nNo data found.")
