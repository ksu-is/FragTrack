# scraper.py
# FragTrack - Siege.gg Data Scraper
# Uses Selenium with smarter waiting for region-specific data

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

# ─── Region URLs ──────────────────────────────────────────────────────────────
REGIONS = {
    "NA":    "https://siege.gg/players?region=NA",
    "EU":    "https://siege.gg/players?region=EU",
    "INTL":  "https://siege.gg/players?region=INTL",
    "APAC":  "https://siege.gg/players?region=APAC",
    "LATAM": "https://siege.gg/players?region=LATAM",
    "MENA":  "https://siege.gg/players?region=MENA",
}

# ─── Setup Chrome Driver ──────────────────────────────────────────────────────
def create_driver():
    options = webdriver.ChromeOptions()
    # Comment out headless so we can SEE what the browser is doing
    # options.add_argument("--headless")
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

# ─── Get First Player Name Visible On Page ────────────────────────────────────
def get_first_player(driver):
    """
    Gets the first player name visible on the page.
    Used to detect when the page has finished loading new region data.
    """
    try:
        rows = driver.find_elements(By.CSS_SELECTOR, "tr[role='row']")
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if cells:
                link = row.find_elements(By.TAG_NAME, "a")
                if link:
                    return link[0].text.strip()
    except:
        return None

# ─── Parse Players ────────────────────────────────────────────────────────────
def parse_players(html, region):
    soup = BeautifulSoup(html, "html.parser")
    players = []
    rows = soup.find_all("tr", role="row")

    for row in rows:
        try:
            name_tag = row.find("td", class_="sp__player position-relative")
            if not name_tag:
                continue
            name = name_tag.find("a").text.strip()
            player_url = name_tag.find("a")["href"]

            rating_tag = row.find("td", class_=lambda c: c and "sp__rating" in c)
            rating = float(rating_tag.text.strip()) if rating_tag else None

            kd_tag = row.find("td", class_="sp__kd")
            kd = kd_tag.text.strip() if kd_tag else None

            maps_tag = row.find("td", class_="sp__map_plays")
            maps = maps_tag.text.strip() if maps_tag else None

            kost_tag = row.find("td", class_=lambda c: c and "sp__kost" in c)
            kost = kost_tag.text.strip() if kost_tag else None

            kpr_tag = row.find("td", class_=lambda c: c and "sp__kpr" in c)
            kpr = kpr_tag.text.strip() if kpr_tag else None

            srv_tag = row.find("td", class_=lambda c: c and "sp__srv" in c)
            srv = srv_tag.text.strip() if srv_tag else None

            plants_tag = row.find("td", class_="sp__plants")
            plants = plants_tag.text.strip() if plants_tag else None

            players.append({
                "name": name,
                "region": region,
                "rating": rating,
                "kd": kd,
                "maps": maps,
                "kost": kost,
                "kpr": kpr,
                "srv": srv,
                "plants": plants,
                "profile_url": "https://siege.gg" + player_url
            })

        except Exception as e:
            print(f"  Skipping row due to error: {e}")
            continue

    return players

# ─── Save to CSV ──────────────────────────────────────────────────────────────
def save_to_csv(players, filename="data/player_data.csv"):
    os.makedirs("data", exist_ok=True)
    df = pd.DataFrame(players)
    df.to_csv(filename, index=False)
    print(f"\n  Saved {len(players)} players to {filename}")

# ─── Main Scraper ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  FragTrack Scraper - Siege.gg (Selenium)")
    print("=" * 50)

    driver = create_driver()
    all_players = []
    previous_first_player = None

    for region, url in REGIONS.items():
        print(f"\nScraping region: {region}")
        try:
            driver.get(url)

            # Wait for table rows to appear
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "tr[role='row']"))
            )

            # Wait for region filter to actually change the content
            # Keep checking until the first player name changes from previous region
            max_attempts = 10
            for attempt in range(max_attempts):
                time.sleep(2)
                first_player = get_first_player(driver)
                print(f"  First player detected: {first_player}")
                if first_player and first_player != previous_first_player:
                    previous_first_player = first_player
                    break
                print(f"  Waiting for region data to load... attempt {attempt + 1}")

            # Final wait to make sure all rows are rendered
            time.sleep(3)

            html = driver.page_source
            players = parse_players(html, region)
            print(f"  Found {len(players)} players in {region}")
            all_players.extend(players)
            time.sleep(2)

        except Exception as e:
            print(f"  Error scraping {region}: {e}")
            continue

    driver.quit()

    if all_players:
        save_to_csv(all_players)
        print("\nScraping complete!")
        print(f"Total players scraped: {len(all_players)}")
    else:
        print("\nNo data found.")
