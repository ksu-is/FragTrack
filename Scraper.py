# scraper.py
# FragTrack - Siege.gg Data Scraper
# Pulls real professional player data from Siege.gg
# scraper.py
# FragTrack - Siege.gg Data Scraper
# Pulls real professional player data from Siege.gg
# Permission granted by Siege.gg for academic use

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

# ─── Headers ─────────────────────────────────────────────────────────────────
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

# ─── Region URLs ──────────────────────────────────────────────────────────────
REGIONS = {
    "NA":   "https://siege.gg/players?date=3+months&region=NA",
    "EU":   "https://siege.gg/players?date=3+months&region=EU",
    "BR":   "https://siege.gg/players?date=3+months&region=BR",
    "LATAM":"https://siege.gg/players?date=3+months&region=LATAM",
    "APAC": "https://siege.gg/players?date=3+months&region=APAC",
    "KR":   "https://siege.gg/players?date=3+months&region=KR",
}

# ─── Fetch Page ───────────────────────────────────────────────────────────────
def get_page(url):
    """
    Sends a request to Siege.gg and returns the raw HTML.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        print(f"  Successfully fetched: {url}")
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching page: {e}")
        return None

# ─── Parse Players ────────────────────────────────────────────────────────────
def parse_players(html, region):
    """
    Parses the HTML and extracts player stats using the real
    class names found from inspecting Siege.gg.
    """
    soup = BeautifulSoup(html, "html.parser")
    players = []

    rows = soup.find_all("tr", role="row")

    for row in rows:
        try:
            # Player Name
            name_tag = row.find("td", class_="sp__player position-relative")
            if not name_tag:
                continue
            name = name_tag.find("a").text.strip()

            # Player URL (to get team info later)
            player_url = name_tag.find("a")["href"]

            # Rating
            rating_tag = row.find("td", class_=lambda c: c and "sp__rating" in c)
            rating = float(rating_tag.text.strip()) if rating_tag else None

            # KD
            kd_tag = row.find("td", class_="sp__kd")
            kd = kd_tag.text.strip() if kd_tag else None

            # Maps
            maps_tag = row.find("td", class_="sp__map_plays")
            maps = maps_tag.text.strip() if maps_tag else None

            # KOST
            kost_tag = row.find("td", class_=lambda c: c and "sp__kost" in c)
            kost = kost_tag.text.strip() if kost_tag else None

            # KPR
            kpr_tag = row.find("td", class_=lambda c: c and "sp__kpr" in c)
            kpr = kpr_tag.text.strip() if kpr_tag else None

            # SRV
            srv_tag = row.find("td", class_=lambda c: c and "sp__srv" in c)
            srv = srv_tag.text.strip() if srv_tag else None

            # Plants
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
    """
    Saves all scraped players to a CSV file.
    """
    os.makedirs("data", exist_ok=True)
    df = pd.DataFrame(players)
    df.to_csv(filename, index=False)
    print(f"\n  Saved {len(players)} players to {filename}")

# ─── Main Scraper ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  FragTrack Scraper - Siege.gg")
    print("=" * 50)

    all_players = []

    for region, url in REGIONS.items():
        print(f"\nScraping region: {region}")
        html = get_page(url)

        if html:
            players = parse_players(html, region)
            print(f"  Found {len(players)} players in {region}")
            all_players.extend(players)
            time.sleep(2)  # Be polite - wait 2 seconds between requests

    if all_players:
        save_to_csv(all_players)
        print("\nScraping complete!")
        print(f"Total players scraped: {len(all_players)}")
    else:
        print("\nNo data found. Check HTML structure.")
