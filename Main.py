# main.py
# FragTrack - Rainbow Six Siege Professional Analytics Dashboard
# Author: [Omar Idris]
# Description: Reads real player data scraped from Siege.gg and runs
#              three original analytical features

import pandas as pd

# ─── Load Player Data ─────────────────────────────────────────────────────────
def load_data(filepath="data/player_data.csv"):
    """
    Loads the scraped player data from the CSV file
    and cleans it for use in all three features.
    """
    try:
        df = pd.read_csv(filepath)

        # Clean KOST - remove % sign and convert to float
        df["kost"] = df["kost"].str.replace("%", "").astype(float)

        # Clean SRV - remove % sign and convert to float
        df["srv"] = df["srv"].str.replace("%", "").astype(float)

        # Clean maps - make sure it's an integer
        df["maps"] = pd.to_numeric(df["maps"], errors="coerce")

        # Clean rating - make sure it's a float
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

        # Drop any rows with missing critical values
        df = df.dropna(subset=["rating", "kost", "maps"])

        print(f"  Loaded {len(df)} players successfully!")
        return df

    except FileNotFoundError:
        print("  Error: player_data.csv not found. Run Scraper.py first.")
        return None

# ─── Load Operator Data ───────────────────────────────────────────────────────
def load_operator_data(filepath="data/operator_data.csv"):
    """
    Loads the scraped operator and yearly performance data.
    """
    try:
        df = pd.read_csv(filepath)

        # Clean rating
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

        # Extract kills from KD string like "82-46 (+36)"
        df["kills"] = df["kd"].str.extract(r"^(\d+)").astype(float)
        df["deaths"] = df["kd"].str.extract(r"-(\d+)").astype(float)
        df["kd_ratio"] = (df["kills"] / df["deaths"]).round(2)

        df = df.dropna(subset=["rating", "kd_ratio"])

        print(f"  Loaded {len(df)} operator records successfully!")
        return df

    except FileNotFoundError:
        print("  Error: operator_data.csv not found. Run operator_scraper.py first.")
        return None

# ─── Feature 1: Underrated Player Detector ───────────────────────────────────
def underrated_player_detector(df):
    """
    Identifies pro players who are performing at an elite level
    but are not getting recognition.

    Criteria:
    - Rating >= 1.20 (elite performer)
    - KOST >= 70% (consistently impacting rounds)
    - Maps <= 15 (low recognition / low play time)
    """
    print("\n" + "=" * 60)
    print("  FRAGTRACK — UNDERRATED PLAYER DETECTOR")
    print("=" * 60)
    print("  Criteria: Rating >= 1.20 | KOST >= 70% | Maps <= 15")
    print("-" * 60)

    underrated = df[
        (df["rating"] >= 1.20) &
        (df["kost"] >= 70.0) &
        (df["maps"] <= 15)
    ].copy()

    underrated = underrated.sort_values("rating", ascending=False)

    if underrated.empty:
        print("\n  No underrated players found with current criteria.")
        print("  Try adjusting the thresholds.")
        return

    print(f"\n  Found {len(underrated)} underrated players:\n")
    print(f"  {'Rank':<5} {'Name':<20} {'Region':<8} {'Rating':<10} {'KOST':<10} {'Maps':<8} {'KD'}")
    print("  " + "-" * 65)

    for i, (_, player) in enumerate(underrated.iterrows(), 1):
        print(f"  {i:<5} {player['name']:<20} {player['region']:<8} "
              f"{player['rating']:<10} {player['kost']:<10} "
              f"{int(player['maps']):<8} {player['kd']}")

    print(f"\n  These {len(underrated)} players have elite stats but low recognition.")
    print("  Consider watching them in upcoming tournaments!")

# ─── Feature 2: Operator Meta Tracker ────────────────────────────────────────
def operator_meta_tracker(op_df):
    """
    Visualizes how operator pick rates have changed year by year
    across the professional scene, showing which operators have
    surged or declined in priority over time.
    """
    print("\n" + "=" * 60)
    print("  FRAGTRACK — OPERATOR META TRACKER")
    print("=" * 60)
    print("  Tracking operator trends from 2020 to 2026")
    print("-" * 60)

    years = sorted(op_df["year"].unique())

    # ── Attack Meta ───────────────────────────────────────────────
    print("\n  ATTACK META — Top 5 Most Picked Operators Per Year:\n")
    print(f"  {'Year':<8}", end="")
    for i in range(1, 6):
        print(f"  {'#' + str(i) + ' Atk':<18}", end="")
    print()
    print("  " + "-" * 98)

    for year in years:
        year_data = op_df[op_df["year"] == year]
        atk_counts = year_data["top_atk_operator"].value_counts().head(5)
        print(f"  {year:<8}", end="")
        for op, count in atk_counts.items():
            print(f"  {op[:12]:<10} ({count}p)  ", end="")
        print()

    # ── Defense Meta ──────────────────────────────────────────────
    print("\n\n  DEFENSE META — Top 5 Most Picked Operators Per Year:\n")
    print(f"  {'Year':<8}", end="")
    for i in range(1, 6):
        print(f"  {'#' + str(i) + ' Def':<18}", end="")
    print()
    print("  " + "-" * 98)

    for year in years:
        year_data = op_df[op_df["year"] == year]
        def_counts = year_data["top_def_operator"].value_counts().head(5)
        print(f"  {year:<8}", end="")
        for op, count in def_counts.items():
            print(f"  {op[:12]:<10} ({count}p)  ", end="")
        print()

    # ── Biggest Meta Shifts ───────────────────────────────────────
    print("\n\n  BIGGEST META SHIFTS (Operators that rose or fell):\n")

    all_atk_ops = op_df["top_atk_operator"].dropna().unique()

    atk_trends = {}
    for op in all_atk_ops:
        counts = []
        for year in years:
            year_data = op_df[op_df["year"] == year]
            count = (year_data["top_atk_operator"] == op).sum()
            counts.append(count)
        atk_trends[op] = counts

    shifts = []
    for op, counts in atk_trends.items():
        if sum(counts) > 5:
            change = counts[-1] - counts[0]
            shifts.append((op, counts[0], counts[-1], change))

    rising = sorted(shifts, key=lambda x: x[3], reverse=True)[:5]
    falling = sorted(shifts, key=lambda x: x[3])[:5]

    print(f"  RISING ATTACK OPERATORS (2020 → 2026):")
    print(f"  {'Operator':<20} {'2020 picks':<15} {'2026 picks':<15} {'Change'}")
    print("  " + "-" * 55)
    for op, first, last, change in rising:
        arrow = "↑" * min(abs(change), 5)
        print(f"  {op:<20} {first:<15} {last:<15} +{change} {arrow}")

    print(f"\n  FALLING ATTACK OPERATORS (2020 → 2026):")
    print(f"  {'Operator':<20} {'2020 picks':<15} {'2026 picks':<15} {'Change'}")
    print("  " + "-" * 55)
    for op, first, last, change in falling:
        arrow = "↓" * min(abs(change), 5)
        print(f"  {op:<20} {first:<15} {last:<15} {change} {arrow}")

# ─── Feature 3: Performance Trend Projector ──────────────────────────────────
def performance_trend_projector(op_df):
    """
    Takes a pro player's rating and KD across their last three
    years and projects their likely performance using a weighted
    average formula.
    Weights: most recent year = 50%, second = 30%, third = 20%
    """
    print("\n" + "=" * 60)
    print("  FRAGTRACK — PERFORMANCE TREND PROJECTOR")
    print("=" * 60)
    print("  Projects player performance using weighted average")
    print("  formula across last 3 years of data.")
    print("-" * 60)

    player_name = input("\n  Enter player name to project (e.g. Stompn): ").strip()

    # Find all years for this player
    player_data = op_df[op_df["player"].str.lower() == player_name.lower()]
    player_data = player_data.sort_values("year", ascending=False)

    if player_data.empty:
        print(f"\n  Player '{player_name}' not found in database.")
        print("  Make sure the name is spelled correctly.")
        return

    if len(player_data) < 2:
        print(f"\n  Not enough historical data for '{player_name}'.")
        print(f"  Only found {len(player_data)} year(s) of data. Need at least 2.")
        return

    # Take last 3 years maximum
    player_data = player_data.head(3)
    years_available = len(player_data)

    # Assign weights based on how many years we have
    if years_available >= 3:
        weights = [0.50, 0.30, 0.20]
    else:
        weights = [0.60, 0.40]

    weights = weights[:years_available]

    # Calculate weighted average rating
    projected_rating = sum(
        row["rating"] * weight
        for (_, row), weight in zip(player_data.iterrows(), weights)
    )

    # Calculate weighted average KD ratio
    projected_kd = sum(
        row["kd_ratio"] * weight
        for (_, row), weight in zip(player_data.iterrows(), weights)
    )

    # Display historical data
    print(f"\n  Historical Performance for {player_name}:\n")
    print(f"  {'Year':<8} {'Rating':<12} {'KD Ratio':<12} {'Atk Op':<15} {'Def Op'}")
    print("  " + "-" * 60)

    for _, row in player_data.iterrows():
        print(f"  {int(row['year']):<8} {row['rating']:<12} "
              f"{row['kd_ratio']:<12} "
              f"{str(row['top_atk_operator']):<15} "
              f"{str(row['top_def_operator'])}")

    # Display projection
    print(f"\n  {'=' * 40}")
    print(f"  PROJECTED PERFORMANCE (Next Tournament):")
    print(f"  {'=' * 40}")
    print(f"  Projected Rating : {projected_rating:.2f}")
    print(f"  Projected KD     : {projected_kd:.2f}")

    # Performance trend indicator
    if years_available >= 2:
        rating_trend = player_data.iloc[0]["rating"] - player_data.iloc[1]["rating"]
        if rating_trend > 0.05:
            trend = "📈 IMPROVING"
        elif rating_trend < -0.05:
            trend = "📉 DECLINING"
        else:
            trend = "➡️  STABLE"
        print(f"  Trend            : {trend}")

    print(f"\n  Weights used: ", end="")
    weight_labels = ["Most recent", "2nd most recent", "3rd most recent"]
    for i, w in enumerate(weights):
        print(f"{weight_labels[i]} ({int(w*100)}%)", end="")
        if i < len(weights) - 1:
            print(" | ", end="")
    print()

# ─── Main Menu ────────────────────────────────────────────────────────────────
def main():
    print("\n" + "=" * 60)
    print("  Welcome to FragTrack!")
    print("  Rainbow Six Siege Pro Analytics Dashboard")
    print("  Data sourced from Siege.gg")
    print("=" * 60)

    # Load both datasets
    print("\n  Loading player data...")
    df = load_data()

    print("  Loading operator data...")
    op_df = load_operator_data()

    if df is None:
        return

    while True:
        print("\n  What would you like to do?")
        print("  [1] Underrated Player Detector")
        print("  [2] Operator Meta Tracker")
        print("  [3] Performance Trend Projector")
        print("  [4] Quit")

        choice = input("\n  Enter choice (1-4): ").strip()

        if choice == "1":
            underrated_player_detector(df)
        elif choice == "2":
            if op_df is not None:
                operator_meta_tracker(op_df)
            else:
                print("  Operator data not available. Run operator_scraper.py first.")
        elif choice == "3":
            if op_df is not None:
                performance_trend_projector(op_df)
            else:
                print("  Operator data not available. Run operator_scraper.py first.")
        elif choice == "4":
            print("\n  Thanks for using FragTrack!")
            break
        else:
            print("  Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()
