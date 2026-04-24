# Sprint 2 FragTrack Project Road Map

#FragTrack Overview:
FragTrack is a Python-based desktop analytics application built around the
professional esports environment of the FPS game Rainbow Six Siege. FragTrack
analyzes pro player and team data sourced from Siege.gg to produce original
insights that are not available on existing platforms. Sites like Siege.gg
record and display raw statistics, but do not interpret or draw conclusions
from that data. FragTrack fills that gap with three original analytical features.

# Core Features
# 1. Underrated Player Detector
Identifies professional players who are statistically performing at an elite
level individually, but are playing for teams with poor win rates — making
them likely undervalued or overlooked by the broader community.

# 2. Operator Meta Tracker
Visualizes how operator pick rates across the professional scene have changed
season by season. Instead of showing what operators are popular right now,
it shows the trajectory — which operators have surged in priority and which
have declined over time.

# 3. Performance Trend Projector
Takes a pro player's statistical performance across their last three seasons
and projects how they are likely to perform in the next tournament using a
weighted average formula to calculate a projected rating and K/D ratio.

#Set up the FragTrack Project structure 
├── main.py                  # Entry point for the application
├── underrated_detector.py   # Underrated Player Detector feature
├── meta_tracker.py          # Operator Meta Tracker feature
├── trend_projector.py       # Performance Trend Projector feature
├── data/
│   └── player_data.json     # Stored player and team data
├── requirements.txt         # Python dependencies
└── projectroadmap.md        # This roadmap file

#created the Main.py file

# Data Sources 
-[Seige.gg](https://siege.gg) — Primary professional stats database
- [R6 Tracker](https://r6.tracker.network) — Secondary stats reference

# Targeted Users
- Rainbow Six Siege Pro League fans
- Aspiring esports coaches and team managers
